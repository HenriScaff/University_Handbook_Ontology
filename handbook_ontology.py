from owlready2 import *






#-------------CREATING ONTOLOGY---------------#

ontology = get_ontology("http://ontology.org/uwa/")
namespace = ontology.get_namespace("http://example.org/uwa/")
graph = default_world.as_rdflib_graph()

with namespace:

	class Unit(Thing): pass

	class Major(Thing): pass

	class hasBridgingUnit(ObjectProperty):
		domain = [Major]
		range = [Unit]

	class RequiredBridgingMajor(Major):
		equivalent_to = [Major & hasBridgingUnit.some(Unit)]

	class hasUnit(ObjectProperty):
		domain = [Major]
		range = [Unit]

	class hasPrerequisite(TransitiveProperty, ObjectProperty):
		domain = [Unit]
		range = [Unit]

	class isPrerequisiteFor(Unit >> Unit): pass
	hasPrerequisite.inverse = isPrerequisiteFor

	class hasAdvisedPriorStudy(TransitiveProperty, ObjectProperty):
		domain = [Unit]
		range = [Unit]

	class isAdvisedPriorStudyFor(Unit >> Unit): pass
	hasAdvisedPriorStudy.inverse = isAdvisedPriorStudyFor

	class code(DataProperty):
		domain = [Thing]
		range = [str]

	class title(DataProperty):
		domain = [Thing]
		range = [str]

	class school(DataProperty):
		domain = [Thing]
		range = [str]		

	class board_of_examiners(DataProperty):
		domain = [Thing]
		range = [str]

	class delivery_mode(DataProperty):
		domain = [Thing]
		range = [str]

	class level(Unit >> int): pass

	class description(DataProperty):
		domain = [Thing]
		range = [str]

	class credit(Unit >> str): pass

	class outcomes(DataProperty):
		domain = [Thing]
		range = [str]

	class assessment(Unit >> str): pass

	class prerequisites_text(Unit >> str): pass

	class prerequisites(Major >> str): pass

	class contact(Unit >> int): pass

	class majors(Unit >> str): pass

	class offering(Unit >> str): pass

	class note(Unit >> str): pass

	class text(DataProperty):
		domain = [Thing]
		range = [str]

	class courses(Major >> str): pass

	rule1 = Imp()
	rule1.set_as_rule("Unit(?u), outcomes(?u, ?o), Major(?m), hasUnit(?m, ?u) -> outcomes(?m, ?o)")

	rule2 = Imp()
	rule2.set_as_rule("Unit(?u), text(?u, ?o), Major(?m), hasUnit(?m, ?u) -> text(?m, ?o)")

print("Saving general ontology to 'handbook_ontology.owl' \n")
ontology.save(file="handbook_ontology.owl", format="rdfxml")







#-------------READING KNOWLEDGE GRAPH DATA---------------#

print("Reading knowledge graph from 'handbook_knowledge_graph.rdf' \n")
with namespace:
	graph.parse("handbook_knowledge_graph.rdf", format='xml')






#-------------QUERYING DATA BEFORE REASONING---------------#

def get_prerequisites_for(unit_iri, graph):
	result = graph.query(
		"""
		PREFIX uwa: <http://example.org/uwa/>

		SELECT ?prereq_code
		WHERE {
			<%s> uwa:hasPrerequisite ?prereq .
			?prereq uwa:code ?prereq_code .
		}
		""" % unit_iri
	)
	return [str(row[0]) for row in result]

math1012_prereqs_before = get_prerequisites_for('http://example.org/uwa/MATH1012', graph)

def num_outcomes_for_major(major_iri, graph):
	result = graph.query(
		"""
		PREFIX uwa: <http://example.org/uwa/>

		SELECT (COUNT(?outcome) AS ?outcome_count)
		WHERE {
			<%s> uwa:outcomes ?outcome ;
				 a uwa:Major .
		}
		""" % major_iri
	)
	return [str(row[0]) for row in result]

software_eng_outcomes_before = num_outcomes_for_major('http://example.org/uwa/MJD-ESOFT', graph)

def num_texts_for_major(major_iri, graph):
	result = graph.query(
		"""
		PREFIX uwa: <http://example.org/uwa/>

		SELECT (COUNT(?text) AS ?text_count)
		WHERE {
			<%s> uwa:text ?text ;
				 a uwa:Major .
		}
		""" % major_iri
	)
	return [str(row[0]) for row in result]

software_eng_texts_before = num_texts_for_major('http://example.org/uwa/MJD-ESOFT', graph)






#-------------INVOKING REASONER, INFERRING DATA---------------#

with namespace:
	sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True)

print("\n")
print("Saving ontology with knowledge graph data and inferred data to 'handbook_ontology.rdf' \n")
file_path = "handbook_ontology.rdf"
ontology.save(file = file_path, format = "rdfxml")






#-------------QUERYING DATA AFTER REASONING---------------#

print("\n")
print("Query Results: \n")

math1012_prereqs_after = get_prerequisites_for('http://example.org/uwa/MATH1012', graph)
print("MATH1012 Prerequisites Before Reasoning:\n\t", math1012_prereqs_before)
print("MATH1012 Prerequisites After Reasoning:\n\t", math1012_prereqs_after)
print("Why? Because hasPrerequisite is now transitive, meaning a prerequisite of a prerequisite is a prerequisite. \n")

print("\n")

software_eng_outcomes_after = num_outcomes_for_major('http://example.org/uwa/MJD-ESOFT', graph)
print("Software Eng Major Outcomes Before Reasoning:\n\t", software_eng_outcomes_before)
print("Software Eng Major Outcomes After Reasoning:\n\t", software_eng_outcomes_after)
print("Why? Because we added a SWRL rule which enforced 'An outcome of a core unit is an outcome of a major'. \n")

print("\n")

software_eng_texts_after = num_texts_for_major('http://example.org/uwa/MJD-ESOFT', graph)
print("Software Eng Major Texts Before Reasoning:\n\t", software_eng_texts_before)
print("Software Eng Major Texts After Reasoning:\n\t", software_eng_texts_after)
print("Why? Because we added a SWRL rule which enforced 'A required text of a core unit is a required text for a major'. \n")






