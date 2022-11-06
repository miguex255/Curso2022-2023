import os

from flask import Flask, render_template, request, json, redirect, url_for, session, jsonify
from flask.wrappers import Response
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
from rdflib.plugins.sparql import prepareQuery
from pathlib import Path
import time



class MyResponse(Response):
    default_mimetype = 'application/json'

# CONFIGURACION DE LA APP
app = Flask(__name__)
app.secret_key = 'clave secreta'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["CACHE_TYPE"] = "null"

# RDFLIB

g = Graph()
g.namespace_manager.bind('rr', Namespace("http://www.w3.org/ns/r2rml#"), override=False)
g.namespace_manager.bind('rml', Namespace("http://semweb.mmlab.be/ns/rml#"), override=False)
g.namespace_manager.bind('ql', Namespace("http://semweb.mmlab.be/ns/ql#"), override=False)
g.namespace_manager.bind('transit', Namespace("http://vocab.org/transit/terms/"), override=False)
g.namespace_manager.bind('xsd', Namespace("http://www.w3.org/2001/XMLSchema#"), override=False)
g.namespace_manager.bind('wgs84_pos', Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#"), override=False)
g.namespace_manager.bind('', Namespace("http://group11.com/"), override=False)
g.namespace_manager.bind('rml', Namespace("http://semweb.mmlab.be/ns/rml#"), override=False)
g.namespace_manager.bind('owl', Namespace("http://www.w3.org/2002/07/owl#"), override=False)

ns = Namespace("http://madridturistsites.es/ontology/")
ns2 = Namespace("http://madridturistsites.es/resource/")
owl = Namespace("http://www.w3.org/2002/07/owl#")
g.parse("./rdf/Monumentos-with-links.nt", format="nt")


# MAIN Y METODOS PARA MOSTRAR PAGINAS
    

@app.route("/")
def main():
    try:
        _jsonList= []
        query = "select distinct ?Object " \
                " where{ ?m <http://madridturistsites.es/ontology/seEncuentraEn>  ?Object.  }"
        q1 = prepareQuery(query)
        for r in g.query(q1):
            data = str(r[0])
            tojson = {'Via': data.replace("http://madridturistsites.es/resource/Via/","")}
            _jsonList.append(tojson)
        with open("./static/streets.json", "w", encoding='utf-8') as file:
            json.dump(_jsonList, file) 
        if(len(_jsonList)==0):
            return render_template("error.html",error="El distrito introducido no es correcto o no existe")
        return render_template("search.html")
    except Exception as e:
        return json.dumps({'error': e})


@app.route("/results", methods=['POST', 'GET'])
def results():
    return render_template("results.html")

@app.route("/busqueda", methods=['POST', 'GET'])
def busqueda():
    try:
        _requestAnho = request.args.get('anho')
        _requestAmbos = request.args.get('ambos')
        _ambos = str(_requestAmbos)
        _anho = str(_requestAnho)
        _request=request.args.get('streetName')
        _streetName=str(_request)
        _streetName = _streetName.upper()
        if _ambos == '0':
            return functionAmbos(_streetName, _anho)
        if len(_anho)>0:
            return functionAnho(_anho)   
        _jsonList= []

        # SPARQL query
        query = "select distinct ?Object " \
                " where{ ?Object <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://madridturistsites.es/ontology/MadridTuristSites/>. " \
                " ?Object <http://madridturistsites.es/ontology/seEncuentraEn> " + "<http://madridturistsites.es/resource/Via/" + _streetName + '>.' + " }"
        q3 = prepareQuery(query)
        for r in g.query(q3):
            tojson = {'id': str(r[0])}
            query2 = "select distinct ?Property " \
                     "where { ?m ?Property ?Object .}"
            q4 = prepareQuery(query2)
            for r2 in g.query(q4, initBindings={"m": r[0]}):
                # print(r[0], r2[0])
                query3 = "select distinct ?Object " \
                         "where { ?m ?p ?Object .}"
                q5 = prepareQuery(query3)
                for r3 in g.query(q5, initBindings={"m": r[0], "p": r2[0]}):
                    propiedad = str(r2[0])
                    objeto = str(r3[0])
                if propiedad != "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    tojson[propiedad.replace("http://madridturistsites.es/ontology/", "")] = objeto
                if propiedad == "http://www.w3.org/2002/07/owl#sameAs":
                    tojson[propiedad.replace("http://www.w3.org/2002/07/owl#sameAs", "parecidoA")] = objeto
                if propiedad == "http://madridturistsites.es/ontology/seEncuentraEn":
                    tojson[propiedad.replace("http://madridturistsites.es/ontology/", "")] = objeto.replace("http://madridturistsites.es/resource/Via/","")
                if propiedad == "http://madridturistsites.es/ontology/autor":
                    queryAutor = "select distinct ?o where {" \
                        "<"+objeto+"> ?p  ?o ."\
                        "?m <http://www.w3.org/2002/07/owl#sameAs> ?o .}"
                    q6 = prepareQuery(queryAutor)
                    for r4 in g.query(q6):
                        tojson["parecidoAutor"] = str(r4[0])
                    tojson[propiedad.replace("http://madridturistsites.es/ontology/", "")] = objeto.replace("http://madridturistsites.es/resource/Autor/","")
            # break
            _jsonList.append(tojson)
        # END SPARQL query
        with open("./static/query.json", "w", encoding='utf-8') as file:
            json.dump(_jsonList, file)
        if(len(_jsonList)==0):
            return render_template("error.html",error="El recurso al que intentas acceder no esta disponible")
        return render_template("results.html",street=_streetName,enlace="https://www.wikidata.org/entity/Q2807", solo = True)
    except Exception as e:
        return json.dumps({'error': e})


def functionAnho(_anho):
    try:
        _jsonList= []
            # SPARQL query
        query = "select distinct ?Object " \
                " where{ ?Object <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://madridturistsites.es/ontology/MadridTuristSites/>. " \
                " ?Object <http://madridturistsites.es/ontology/construidoEn> ?year " \
                "FILTER('"+_anho+"'>=str(?year))}"
        q3 = prepareQuery(query)
        for r in g.query(q3):
            tojson = {'id': str(r[0])}
            query2 = "select distinct ?Property " \
                     "where { ?m ?Property ?Object .}"
            q4 = prepareQuery(query2)
            for r2 in g.query(q4, initBindings={"m": r[0]}):
                # print(r[0], r2[0])
                query3 = "select distinct ?Object " \
                         "where { ?m ?p ?Object .}"
                q5 = prepareQuery(query3)
                for r3 in g.query(q5, initBindings={"m": r[0], "p": r2[0]}):
                    propiedad = str(r2[0])
                    objeto = str(r3[0])
                if propiedad != "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    tojson[propiedad.replace("http://madridturistsites.es/ontology/", "")] = objeto
                if propiedad == "http://www.w3.org/2002/07/owl#sameAs":
                    tojson[propiedad.replace("http://www.w3.org/2002/07/owl#sameAs", "parecidoA")] = objeto
                if propiedad == "http://madridturistsites.es/ontology/seEncuentraEn":
                    tojson[propiedad.replace("http://madridturistsites.es/ontology/", "")] = objeto.replace("http://madridturistsites.es/resource/Via/","")
                if propiedad == "http://madridturistsites.es/ontology/autor":
                    queryAutor = "select distinct ?o where {" \
                        "<"+objeto+"> ?p  ?o ."\
                        "?m <http://www.w3.org/2002/07/owl#sameAs> ?o .}"
                    q6 = prepareQuery(queryAutor)
                    for r4 in g.query(q6):
                        tojson["parecidoAutor"] = str(r4[0])
                    tojson[propiedad.replace("http://madridturistsites.es/ontology/", "")] = objeto.replace("http://madridturistsites.es/resource/Autor/","")
            # break
            _jsonList.append(tojson)
        # END SPARQL query
        with open("./static/query.json", "w", encoding='utf-8') as file:
            json.dump(_jsonList, file)
        if(len(_jsonList)==0):
            return render_template("error.html",error="El recurso al que intentas acceder no esta disponible")
        return render_template("results.html", anho = _anho, solo = False)
    except Exception as e:
        return json.dumps({'error': e})

def functionAmbos(_streetName,_anho):
    try:
        _jsonList= []
            # SPARQL query
        query = "select distinct ?Object " \
                " where{ ?Object <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://madridturistsites.es/ontology/MadridTuristSites/>. " \
                " ?Object <http://madridturistsites.es/ontology/seEncuentraEn> " + "<http://madridturistsites.es/resource/Via/" + _streetName + '>.'\
                " ?Object <http://madridturistsites.es/ontology/construidoEn> ?year " \
                "FILTER('"+_anho+"'>=str(?year))}"
        q3 = prepareQuery(query)
        for r in g.query(q3):
            tojson = {'id': str(r[0])}
            query2 = "select distinct ?Property " \
                     "where { ?m ?Property ?Object .}"
            q4 = prepareQuery(query2)
            for r2 in g.query(q4, initBindings={"m": r[0]}):
                # print(r[0], r2[0])
                query3 = "select distinct ?Object " \
                         "where { ?m ?p ?Object .}"
                q5 = prepareQuery(query3)
                for r3 in g.query(q5, initBindings={"m": r[0], "p": r2[0]}):
                    propiedad = str(r2[0])
                    objeto = str(r3[0])
                if propiedad != "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    tojson[propiedad.replace("http://madridturistsites.es/ontology/", "")] = objeto
                if propiedad == "http://www.w3.org/2002/07/owl#sameAs":
                    tojson[propiedad.replace("http://www.w3.org/2002/07/owl#sameAs", "parecidoA")] = objeto
                if propiedad == "http://madridturistsites.es/ontology/seEncuentraEn":
                    tojson[propiedad.replace("http://madridturistsites.es/ontology/", "")] = objeto.replace("http://madridturistsites.es/resource/Via/","")
                if propiedad == "http://madridturistsites.es/ontology/autor":
                    queryAutor = "select distinct ?o where {" \
                        "<"+objeto+"> ?p  ?o ."\
                        "?m <http://www.w3.org/2002/07/owl#sameAs> ?o .}"
                    q6 = prepareQuery(queryAutor)
                    for r4 in g.query(q6):
                        tojson["parecidoAutor"] = str(r4[0])
                    tojson[propiedad.replace("http://madridturistsites.es/ontology/", "")] = objeto.replace("http://madridturistsites.es/resource/Autor/","")
            # break
            _jsonList.append(tojson)
        # END SPARQL query
        with open("./static/query.json", "w", encoding='utf-8') as file:
            json.dump(_jsonList, file)
        if(len(_jsonList)==0):
            return render_template("error.html",error="El recurso al que intentas acceder no esta disponible")
        return render_template("results.html",street=_streetName,enlace="https://www.wikidata.org/entity/Q2807", anho = _anho, ambos = True)
    except Exception as e:
        return json.dumps({'error': e})
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(port=5000)
