import json
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, FOAF, XSD, DC
from rdflib import BNode
from pyshacl import validate




#--------------CREATING THE GRAPH------------#

#Import the units data from file
with open('units.json', 'r') as file:
    units_data = json.load(file)

#Import the majors data from file
with open('majors.json', 'r') as file:
    majors_data = json.load(file)

#Create a new namespace for the UWA-related properties, and import SCHEMA
UWA = Namespace("http://example.org/uwa/")
SCHEMA = Namespace("http://schema.org/")

#Create graph
g = Graph()

#Integrating namespaces
g.bind("rdf", RDF)
g.bind("uwa", UWA)
g.bind("schema", SCHEMA)
g.bind("dc", DC)
g.bind("foaf", FOAF)
g.bind("xsd", XSD)

#Create Unit Entities and Types
for unit in units_data.keys():
    unit_uri = UWA[unit]
    g.add((unit_uri, RDF.type, UWA.Unit))

#Create Major Entities and Types
for major in majors_data.keys():
    major_uri = UWA[major]
    g.add((major_uri, RDF.type, UWA.Major))

#Adding Properties/Relations for Units
for unit, unit_data in units_data.items():
	for property_name, value in unit_data.items():
		if property_name == "contact" and isinstance(value, dict):
			total_contact_hours = sum(int(v) for v in value.values())
			g.add((UWA[unit], UWA[property_name], Literal(total_contact_hours, datatype=XSD.integer)))
			continue
		value_list = value if isinstance(value, list) else [value]
		if property_name == "prerequisites_cnf":
			for disjunct in value_list:
				for item in disjunct:
					g.add((UWA[item], RDF.type, UWA.Unit))
					g.add((UWA[item], UWA.code, Literal(str(item), datatype=XSD.string)))
					g.add((UWA[item], UWA.level, Literal(int(item[4]))))
					g.add((UWA[unit], UWA.hasPrerequisite, UWA[item])) ###
		elif property_name == "advisable_prior_study":
			for item in value_list:
				g.add((UWA[item], RDF.type, UWA.Unit))
				g.add((UWA[item], UWA.code, Literal(str(item), datatype=XSD.string)))
				g.add((UWA[item], UWA.level, Literal(int(item[4]))))
				g.add((UWA[unit], UWA.hasAdvisedPriorStudy, UWA[item])) ###
		elif property_name == "level":
			property_uri = UWA[property_name]
			for item in value_list:
				g.add((UWA[unit], property_uri, Literal(int(item), datatype=XSD.integer)))
		else:
			property_uri = UWA[property_name]
			for item in value_list:
				g.add((UWA[unit], property_uri, Literal(str(item), datatype=XSD.string)))

#Adding Properties/Relations for Majors
for major, major_data in majors_data.items():
	for property_name, value in major_data.items():
		value_list = value if isinstance(value, list) else [value]
		if property_name == "bridging":
			for item in value_list:
				g.add((UWA[item], RDF.type, UWA.Unit))
				g.add((UWA[item], UWA.code, Literal(str(item), datatype=XSD.string)))
				g.add((UWA[item], UWA.level, Literal(int(item[4]))))
				g.add((UWA[major], UWA.hasBridgingUnit, UWA[item])) ###
		elif property_name == "units":
			for item in value_list:
				g.add((UWA[item], RDF.type, UWA.Unit))
				g.add((UWA[item], UWA.code, Literal(str(item), datatype=XSD.string)))
				g.add((UWA[item], UWA.level, Literal(int(item[4]))))
				g.add((UWA[major], UWA.hasUnit, UWA[item])) ###
		else:
			property_uri = UWA[property_name]
			for item in value_list:
				g.add((UWA[major], property_uri, Literal(str(item), datatype=XSD.string)))






#--------------EXPORTING THE GRAPH------------#

print("Writing graph to files. \n")

ttl_data = g.serialize(format='turtle')
if isinstance(ttl_data, str):
    ttl_data = ttl_data.encode('utf-8')
with open('handbook_knowledge_graph.ttl', 'wb') as f:
    f.write(ttl_data)

rdf_xml_data = g.serialize(format='xml')
if isinstance(rdf_xml_data, str):
    rdf_xml_data = rdf_xml_data.encode('utf-8')
with open('handbook_knowledge_graph.rdf', 'wb') as f:
    f.write(rdf_xml_data)








#----------------QUERYING THE GRAPH----------------#
print("Querying the graph. \n")



print("\n----------------QUERY 1----------------\n")
print("Find all units with more than 6 outcomes.\n")
query1 = """
	PREFIX uwa: <http://example.org/uwa/>

	SELECT ?unit_code
	WHERE {
		?unit a uwa:Unit;
			  uwa:code ?unit_code.
		{
			SELECT ?unit (COUNT(?outcome) AS ?num_outcomes)
			WHERE {
				?unit uwa:outcomes ?outcome.
		  	}
			GROUP BY ?unit
		}
	  	FILTER (?num_outcomes > 6)
	}
"""
i = 0
for row in g.query(query1):
	print("\t", row["unit_code"])
	i += 1
print("A TOTAL OF", i, "UNITS HAVE MORE THAN 6 OUTCOMES\n")




print("\n----------------QUERY 2----------------\n")
print("Find all level 3 units that do not have an exam, and where none of their prerequisites have an exam.\n")
query2 = """
	PREFIX uwa: <http://example.org/uwa/>

	SELECT DISTINCT ?unit_code
	WHERE {
		?unit a uwa:Unit;
			  uwa:level 3;
			  uwa:code ?unit_code.
		FILTER NOT EXISTS {
			?unit uwa:assessment ?assessment.
			FILTER (CONTAINS(LCASE(STR(?assessment)), "exam"))
		}
		OPTIONAL {
			?unit uwa:hasPrerequisite ?prereq.
			FILTER NOT EXISTS {
				?prereq uwa:assessment ?prereqAssessment.
				FILTER (CONTAINS(LCASE(STR(?prereqAssessment)), "exam"))
			}
		}
	}
"""
i = 0
for row in g.query(query2):
	print("\t", row["unit_code"])
	i += 1
print("A TOTAL OF", i, "LEVEL 3 UNITS HAVE NO EXAM, AND HAVE NO PREREQS WITH EXAMS\n")




print("\n----------------QUERY 3----------------\n")
print("Find all units that appear in more than 3 majors.\n")
query3 = """
	PREFIX uwa: <http://example.org/uwa/>

	SELECT ?unit_code (COUNT(?unit_code) AS ?major_count)
	WHERE {
		?major a uwa:Major;
			   uwa:hasUnit ?unit.
		?unit a uwa:Unit;
		      uwa:code ?unit_code.
	}
	GROUP BY ?unit_code
	HAVING (COUNT(?unit_code) > 3)
"""
i = 0
for row in g.query(query3):
	print("\t", row["unit_code"])
	print("\t\tNumber of Majors:", row["major_count"])
	i += 1
print("A TOTAL OF", i, "UNITS APPEAR IN MORE THAN 3 MAJORS\n")




print("\n----------------QUERY 4----------------\n")
print("Basic search functionality: Given a query string (eg \"environmental policy\"), can you find the units that contain this string in the description or outcomes?\n")
def generate_search_query(search_string):
	base_query = """
	PREFIX uwa: <http://example.org/uwa/>

	SELECT DISTINCT ?unit_code
	WHERE {{
		?unit a uwa:Unit;
				uwa:code ?unit_code;
				OPTIONAL {{ ?unit uwa:description ?description. }}
				OPTIONAL {{ ?unit uwa:outcomes ?outcomes. }}
				
		FILTER (
			(BOUND(?description) && CONTAINS(LCASE(STR(?description)), "{0}"))
			||
			(BOUND(?outcomes) && CONTAINS(LCASE(STR(?outcomes)), "{0}"))
		)
	}}
	"""
	return base_query.format(search_string.lower())

#Example usage:
search_string = "environmental policy"
query4 = generate_search_query(search_string)
i = 0
for row in g.query(query4):
	print("\t", row["unit_code"])
	i += 1
print("A TOTAL OF", i, "UNITS CONTAIN \'" + search_string + "\' IN THEIR OUTCOMES OR DESCRIPTION\n")
	






print("\n----------------QUERY 5----------------\n")
print("Find the top 10 highest level units at UWA.\n")
query5 = """
	PREFIX uwa: <http://example.org/uwa/>

	SELECT ?unit ?level
	WHERE {
	    ?unit a uwa:Unit;
	          uwa:level ?level .
	}
	ORDER BY DESC(?level)
	LIMIT 10
"""
for row in g.query(query5):
	print("\tUnit:", row["unit"])
	print("\tLevel:", row["level"], "\n")



