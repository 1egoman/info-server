MAX_DEPTH = 10

def ingest(data, maxdepth=MAX_DEPTH, depth=0, datumType=None, prev=None):
    datumType = type(data)

    node = None
    if datumType is str:
        node = TextDatum(data, depth=depth, maxdepth=maxdepth, prev=prev)
    elif datumType is int:
        node = NumberDatum(data, depth=depth, maxdepth=maxdepth, prev=prev)
    else:
        raise Exception("Dont know which datum type to make!")

    if prev:
        prev.next = node

    node.calculate()
    return node


class Datum(object):
    def __init__(self, seed_data, depth=0, maxdepth=None, prev=None):
        self.next = None
        self.prev = prev
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

                # Add a new Datum
                if self.maxdepth and self.depth + 1 < self.maxdepth:
                    ingest(value, maxdepth=self.maxdepth, depth=self.depth+1, prev=self)

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.data)



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


d = ingest("blablablaaegagankgjnao;glane;eogze")

node = d
while node:
    print node
    node = node.next
