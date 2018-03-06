from .base_datum import Datum

from ..concepts import Concept, Relation

class TextDatum(Datum):
    def calculate_length(self):
        return len(self.data["input"])

    def calculate_number_of_words(self):
        return len(self.data["input"].split(' '))

    def calculate_similar_concepts(self):
        concept = Concept.find(self.data["input"])
        if concept is None:
            return None

        RELATION_DATUM_TYPES = {
            "SYNONYM": SynonymRelationDatum,
            "ANTONYM": AntonymRelationDatum,
            "IDENTICAL": IdenticalRelationDatum,
            "SUBSET": SubsetRelationDatum,
            "SUPERSET": SupersetRelationDatum,
        }

        relations = concept.relations()

        return [RELATION_DATUM_TYPES[relation.kind](relation) for relation in relations]

class RelationDatum(Datum):
    def preprocess_data(self, seed_data):
        return [concept for concept in seed_data.concepts if concept]

    # Returns an array of concepts
    def calculate_concepts(self):
        return [concept.name for concept in self.data["input"]]

class SynonymRelationDatum(RelationDatum): pass
class AntonymRelationDatum(RelationDatum): pass
class IdenticalRelationDatum(RelationDatum): pass
class SubsetRelationDatum(RelationDatum): pass
class SupersetRelationDatum(RelationDatum): pass
