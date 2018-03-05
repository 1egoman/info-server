import sqlite3
db = sqlite3.connect('./concepts.db')
cursor = db.cursor()


RELATIONS = {
    "SYNONYM": "SYNONYM",
    "ANTONYM": "ANTONYM",
    "IDENTICAL": "IDENTICAL",
    "SUBSET": "SUBSET",
    "SUPERSET": "SUPERSET",
}

class Relation(object):
    def __init__(self, concept, kind, *args):
        self.id = None

        self.concept = concept
        self.kind = kind
        self.concepts = list(args)

    def save(self):
        if self.id is not None:
            cursor.execute(
                'UPDATE relations SET concept = ?, kind = ?, concept0 = ?, concept1 = ?, concept2 = ?, concept3 = ?, concept4 = ?, concept5 = ? WHERE id = ?',
                (self.concept.id,
                self.kind,
                self.concepts[0].id if len(self.concepts) >= 1 else -1,
                self.concepts[1].id if len(self.concepts) >= 2 else -1,
                self.concepts[2].id if len(self.concepts) >= 3 else -1,
                self.concepts[3].id if len(self.concepts) >= 4 else -1,
                self.concepts[4].id if len(self.concepts) >= 5 else -1,
                self.concepts[5].id if len(self.concepts) >= 6 else -1,
                self.id),
            )
        else:
            cursor.execute(
                '''INSERT INTO relations (
                    concept,
                    kind,
                    concept0,
                    concept1,
                    concept2,
                    concept3,
                    concept4,
                    concept5
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (self.concept.id,
                self.kind,
                self.concepts[0].id if len(self.concepts) >= 1 else -1,
                self.concepts[1].id if len(self.concepts) >= 2 else -1,
                self.concepts[2].id if len(self.concepts) >= 3 else -1,
                self.concepts[3].id if len(self.concepts) >= 4 else -1,
                self.concepts[4].id if len(self.concepts) >= 5 else -1,
                self.concepts[5].id if len(self.concepts) >= 6 else -1),
            )
            self.id = cursor.lastrowid

        db.commit()
