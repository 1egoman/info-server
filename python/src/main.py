from datum.ingest import ingest
from datum import Datum

ingest("A")
ingest("B")
ingest("C")

print(Datum.current_datum)
