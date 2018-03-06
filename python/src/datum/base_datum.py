import numpy as np

class Pipeline(object):
    def __init__(self):
        self.current_datum = None

    def count(self):
        count = 0
        pointer = self.current_datum

        while pointer:
            count += 1
            pointer = pointer.prev

        return count

    def debug(self):
        pointer = self.current_datum
        while pointer:
            print(pointer)
            pointer = pointer.prev

    # A generator for looping through all datums in a pipeline
    def items(self):
        pointer = self.current_datum
        while pointer:
            yield pointer
            pointer = pointer.prev

    # Get the neth value in a pipeline. This is relatively slow for a large pipeline, so really only
    # useful in debugging.
    def nth(self, n):
        for index, item in enumerate(self.items()):
            if index == n:
                return item

class Datum(object):
    default_pipeline = Pipeline()

    def __init__(self, seed_data, depth=0, maxdepth=None, pipeline=None):
        self.next = None
        self.prev = None
        self.data = {"input": self.preprocess_data(seed_data)}

        self.depth = depth
        self.maxdepth = maxdepth

        if pipeline is not None:
            self.pipeline = pipeline
        else:
            self.pipeline = Datum.default_pipeline

        from .ingest import ingest
        self.ingest = ingest

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
                            self.ingest(v, depth=self.depth+1, pipeline=self.pipeline)
                    else:
                        # Ingest a single value
                        self.ingest(value, depth=self.depth+1, pipeline=self.pipeline)

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, self.data)
