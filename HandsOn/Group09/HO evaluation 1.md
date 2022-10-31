9
    Analysis
        - The URIs in the resource naming strategy should not contain version numbers.
        - There is no need to have different paths for classes and properties in the ontology.
    Ontology
        - Do not create the ontology by hand. It has errors that could have been solved if you used a tool.
        - The names of the ontology terms are not correct because the namespace is not defined correctly.
        - Even if IRIs allow to use accented words, I would not  create URIs with accents. You can leave the accents in the description of the resource, though.
        - Some of the properties defined with numbers as ranges are not numbers.
        - Some ranges of datatype properties are wrong.
        - In OWL, there are object properties (where value of the property is a resource) and datatype properties (where the value of the property is a string literal, usually typed). You are using object properties for everything.
    RDF data
        - The URIs of resources are wrong (they include "~iri").
        - The types of monuments are wrong.
        - The types of streets are wrong.
        - Neighbourhoods are not generated correctly.
        - Make URIs more readable removing spaces, accents, etc.
