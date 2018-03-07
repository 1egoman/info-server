import sqlite3
db = sqlite3.connect('./concepts.db')
cursor = db.cursor()

import pickle

import spacy
nlp = spacy.load('en')
def stemmer(word):
    return nlp(word)[0].lemma_

from .relation import Relation
from .metadata import Metadata

class Concept(object):
    def __init__(self, name, subtype):
        self.id = None

        self.name = stemmer(name)
        self.subtype = subtype

    def save(self):
        if self.id is not None:
            cursor.execute(
                'UPDATE concepts SET name = ?, subtype = ? WHERE id = ?',
                (self.name, self.subtype, self.id)
            )
        else:
            cursor.execute(
                'INSERT INTO concepts (name, subtype) VALUES (?, ?)',
                (self.name, self.subtype)
            )
            self.id = cursor.lastrowid

        db.commit()
        return self

    @staticmethod
    def get(id):
        cursor.execute(
            'SELECT id, name, subtype from concepts where id = ? LIMIT 1',
            (id,)
        )
        rows = cursor.fetchall()

        if len(rows) > 0:
            concept = Concept(rows[0][1], rows[0][2])
            concept.id = rows[0][0]
            concept.saved = True
            return concept
        else:
            return None

    @staticmethod
    def find(phrase, subtype=None):
        print('FIND', phrase, subtype)
        if subtype is not None:
            cursor.execute(
                'SELECT id from concepts where name = ? AND subtype = ? LIMIT 1',
                (stemmer(phrase), subtype)
            )
        else:
            cursor.execute(
                'SELECT id from concepts where name = ? LIMIT 1',
                (stemmer(phrase),)
            )
        rows = cursor.fetchall()
        print(rows)

        if len(rows) > 0:
            return Concept.get(rows[0][0])
        else:
            return None

    def relations(self):
        cursor.execute(
            'SELECT id,kind,concept0,concept1,concept2,concept3,concept4,concept5 from relations where concept = ?',
            (self.id,)
        )
        rows = cursor.fetchall()

        output = []
        for row in rows:
            concepts = []
            for concept in row[2:]:
                concepts.append(Concept.get(concept))

            relation = Relation(
                self,
                row[1],
                *concepts,
            )
            relation.id = row[0]
            relation.saved = True
            output.append(relation)

        return output

    # Recursively return all relationships (to a certain depth) that relate to `self`.
    def deep_relations(self, depth=3):
        if depth == 0:
            return {}

        relations = self.relations()

        output = {}
        for relation in relations:
            related = relation.concepts[0].deep_relations(depth-1)
            output[relation.concepts[0].name] = related

        return output

    def add_relation(self, kind, *concepts):
        relation = Relation(self, kind, *concepts)
        relation.save()
        return relation

    def metadata(self):
        cursor.execute(
            'SELECT id,kind,data from metadata where concept = ?',
            (self.id,)
        )
        rows = cursor.fetchall()

        output = []
        for row in rows:
            meta = Metadata(
                self,
                row[1],
                pickle.loads(row[2]),
            )
            meta.id = row[0]
            meta.saved = True
            output.append(meta)

        return output

    def add_metadata(self, kind, data):
        meta = Metadata(self, kind, data)
        meta.save()
        return meta
