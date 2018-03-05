import sqlite3
db = sqlite3.connect('./concepts.db')
cursor = db.cursor()

import pickle

from .relation import Relation

METADATA = {
    "RELATED_IMAGE": "RELATED_IMAGE",
}

class Metadata(object):
    def __init__(self, concept, kind, data):
        self.id = None

        if not concept:
            raise Exception('Metadata items must reference a concept')

        self.concept = concept
        self.kind = kind
        self.data = data

    def save(self):
        data = pickle.dumps(self.data)

        if self.id is not None:
            cursor.execute(
                'UPDATE metadata SET kind = ?, data = ? WHERE id = ?',
                (self.kind, data, self.id)
            )
        else:
            cursor.execute(
                'INSERT INTO metadata (concept, kind, data) VALUES (?, ?, ?)',
                (self.concept.id, self.kind, data)
            )
            self.id = cursor.lastrowid

        db.commit()

