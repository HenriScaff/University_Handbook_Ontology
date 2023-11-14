import json
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, FOAF, XSD, DC
from rdflib import BNode
from pyshacl import validate

#----------------VALIDATION OF KNOWLEDGE GRAPH----------------#

g = Graph().parse('handbook_knowledge_graph.ttl', format='turtle')
s = Graph().parse('handbook_shapes.ttl', format='turtle')

results = validate(
	g,
	shacl_graph=s,
	inference='both'
)

(conforms, results_graph, results_text) = results
if not conforms:
	print(results_text)
	exit()
print(results_text)