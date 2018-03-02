MAX_DEPTH = 10

def ingest(data, depth=0, datumType=None):
    datumType = type(data)

    # Figure out how to ingest the data
    node = None
    if datumType is str:
        node = TextDatum(data, depth=depth, maxdepth=MAX_DEPTH)
    elif datumType is int:
        node = NumberDatum(data, depth=depth, maxdepth=MAX_DEPTH)
    else:
        raise Exception("Dont know which datum type to make!")

    # Derive other properties of the node. Add them to the pipeline before the current node.
    node.calculate()
# Link node to right side of Datum.current_datum node.prev = Datum.current_datum
    if Datum.current_datum:
        Datum.current_datum.next = node
    Datum.current_datum = node


    return node


class Datum(object):
    current_datum = None

    def __init__(self, seed_data, depth=0, maxdepth=None):
        self.next = None
        self.prev = None
        self.data = {"input": self.preprocess_data(seed_data)}

        self.depth = depth
        self.maxdepth = maxdepth

    def preprocess_data(self, seed_data):
        return seed_data

    def calculate(self):
        for i in dir(self):
            if i.startswith("calculate_"):
                # Set the attribute on the Datum
                value = getattr(self, i)()
                self.data[i[len("calculate_"):]] = value

                # Add a new Datum, ensuring that we only recurse so deep and that duplicates should
                # be avoided.
                if (
                    self.maxdepth and self.depth + 1 < self.maxdepth
                ) and (
                    self.data["input"] != value
                ):
                    ingest(value, depth=self.depth+1)

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, self.data)



class TextDatum(Datum):
    def calculate_length(self):
        return len(self.data["input"])

    def calculate_number_of_words(self):
        return len(self.data["input"].split(' '))

    # def calculate_letter_frequency(self):
    #     value = self.data["input"]
    #
    #     frequencies = {}
    #
    #     for i in value.split():
    #         if frequencies.get(i):
    #             frequencies[i] += 1
    #         else:
    #             frequencies[i] = 1
    #
    #     1

class NumberDatum(Datum):
    def calculate_scale(self):
        value = self.data["input"]
        power_of_ten = 0

        while value >= 1:
            power_of_ten += 1
            value /= 10

        return power_of_ten








ingest("a")
ingest("b")

ingest("c")
ingest("bla")
ingest("a")
ingest("b")

ingest("bla")
ingest("z")
ingest("a")
ingest("b")

ingest("c")
ingest("a")
ingest("b")

print()
print()

node = Datum.current_datum
while node:
    print( node)
    node = node.prev

print()
print()

print( "PATTERN")
import attempt_2
pattern = attempt_2.pattern(Datum.current_datum)
print( pattern)

# print()
# print( "MATCHES PATTERN")
# print( matches_pattern(Datum.current_datum, pattern))
#
# # print( node_similarity(TextDatum("abcd"), TextDatum("abd")))
