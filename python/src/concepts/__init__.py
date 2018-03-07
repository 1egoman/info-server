import sqlite3
db = sqlite3.connect('./concepts.db')
cursor = db.cursor()

from .concept import Concept
from .relation import Relation, RELATIONS

def migrate():
    print("* Initializing database...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            subtype TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept INTEGER REFERENCES concepts(id),
            kind TEXT,
            concept0 INTEGER REFERENCES concepts(id),
            concept1 INTEGER REFERENCES concepts(id),
            concept2 INTEGER REFERENCES concepts(id),
            concept3 INTEGER REFERENCES concepts(id),
            concept4 INTEGER REFERENCES concepts(id),
            concept5 INTEGER REFERENCES concepts(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept INTEGER REFERENCES concepts(id),
            kind TEXT,
            data BLOB
        )
    ''')
    print("* Database initialized.")
