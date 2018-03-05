from concepts import migrate, Concept, Relation
migrate()

# from concepts.train.vocab import train
from concepts.train.metadata import train

# c = Concept("foo", "noun")
# c.save()
# c.add_metadata('BLABLABLA', 'foobarbaz')
#
# print(c.metadata())
# print()
#
# b = Concept("bar", "noun")
# b.save()
#
# c.add_relation("SYNONYM", b)
# print(c.relations())

b = Concept("balloon", "noun")
b.save()

train(b)
