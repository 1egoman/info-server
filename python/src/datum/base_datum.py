
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
        for i in sorted(dir(self)):
            if i.startswith("calculate_"):
                # Set the attribute on the Datum
                value = getattr(self, i)()
                if value is None: continue
                self.data[i[len("calculate_"):]] = value

                # Add a new Datum, ensuring that we only recurse so deep and that duplicates should
                # be avoided.
                if (
                    self.maxdepth and self.depth + 1 < self.maxdepth
                ) and (
                    type(self.data["input"]) is np.ndarray or self.data["input"] != value
                ):
                    if type(value) is list:
                        # Ingest an array of values one at a time
                        for v in value:
                            ingest(v, depth=self.depth+1)
                    else:
                        # Ingest a single value
                        ingest(value, depth=self.depth+1)

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, self.data)
