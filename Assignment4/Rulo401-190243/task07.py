# -*- coding: utf-8 -*-
"""Task07.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tV5j-DRcpPtoJGoMj8v2DSqR_9wyXeiE

**Task 07: Querying RDF(s)**
"""

!pip install rdflib 
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2020-2021/master/Assignment4"

"""Leemos el fichero RDF de la forma que lo hemos venido haciendo"""

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.namespace_manager.bind('vcard', Namespace("http://www.w3.org/2001/vcard-rdf/3.0#"), override=False)
g.parse(github_storage+"/resources/example6.rdf", format="xml")

"""**TASK 7.1: List all subclasses of "Person" with RDFLib and SPARQL**"""

from rdflib.plugins.sparql import prepareQuery
ns = Namespace("http://somewhere#")

for s,p,o in g.triples((None, RDFS.subClassOf, ns.Person)):
  print(s)

q1 = prepareQuery('''
  SELECT ?Subclasses WHERE { 
    ?Subclasses RDFS:subClassOf ns:Person. 
  }
  ''',
  initNs = { "ns": ns, "RDFS": RDFS}
)

for r in g.query(q1):
  print(r.Subclasses)

"""**TASK 7.2: List all individuals of "Person" with RDFLib and SPARQL (remember the subClasses)**"""

for s,p,o in g.triples((None, RDF.type, ns.Person)):
  print(s)
pSubclass = g.triples((None, RDFS.subClassOf, ns.Person))
for s,p,o in pSubclass:
  people = g.triples((None, RDF.type, s))
  for s,p,o in people:
    print(s)


q2 = prepareQuery('''
  SELECT DISTINCT ?Person WHERE { 
    {?Person RDF:type ns:Person} UNION
    {?Person RDF:type ?Class.
    ?Class  RDFS:subClassOf ns:Person}
  }
  ''',
  initNs = { "ns": ns, "RDF": RDF, "RDFS": RDFS}
)


for r in g.query(q2):
  print(r.Person)

"""**TASK 7.3: List all individuals of "Person" and all their properties including their class with RDFLib and SPARQL**"""

for s,p,o in g.triples((None, RDF.type, ns.Person)):
  for s,p,o in g.triples((s,None,None)):
    print(s,p)
pSubclass = g.triples((None, RDFS.subClassOf, ns.Person))
for s,p,o in pSubclass:
  people = g.triples((None, RDF.type, s))
  for s,p,o in people:
    for s,p,o in g.triples((s,None,None)):
      print(s,p)


q3 = prepareQuery('''
  SELECT ?Person (GROUP_CONCAT(?Property ; separator=" | ") as ?Properties) WHERE{
    ?Person ?Property ?Value.
    {
        SELECT DISTINCT ?Person WHERE { 
        {?Person RDF:type ns:Person} UNION
        {?Person RDF:type ?Class.
        ?Class  RDFS:subClassOf ns:Person}
        }
    }
  }GROUP BY ?Person
  ''',
  initNs = { "ns": ns, "RDF": RDF, "RDFS": RDFS}
)


for r in g.query(q3):
  print(r.Person,r.Properties)