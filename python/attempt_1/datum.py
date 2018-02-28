import cv2
import numpy as np;

MAX_DEPTH = 10

def ingest(data, depth=0, datumType=None):
    datumType = type(data)

    # Figure out how to ingest the data
    node = None
    # "Hello World"
    if datumType is str:
        node = TextDatum(data, depth=depth, maxdepth=MAX_DEPTH)

    # 5 or 3.28
    elif datumType is int or datumType is float:
        node = NumberDatum(data, depth=depth, maxdepth=MAX_DEPTH)

    # ((1, 1), (2, 2))
    elif datumType is tuple and len(data) in [2, 3] and type(data[0]) is tuple:
        node = PointDatum(data, depth=depth, maxdepth=MAX_DEPTH)

    # (1, 1)
    elif datumType is tuple and len(data) in [2, 3]:
        node = PointDatum(data, depth=depth, maxdepth=MAX_DEPTH)

    elif datumType is np.ndarray and len(data.shape) == 3:
        node = ImageDatum(data, depth=depth, maxdepth=MAX_DEPTH)
    else:
        raise Exception("Dont know which datum type to make!")

    # Derive other properties of the node. Add them to the pipeline before the current node.
    node.calculate()

    # Link node to right side of Datum.current_datum
    node.prev = Datum.current_datum
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

    def calculate_rounded(self):
        if type(self.data["input"]) is int:
            return None

        fractional = self.data["input"] - int(self.data["input"])
        if fractional > 0.5:
            return int(self.data["input"]) + 1
        else:
            return int(self.data["input"])

    def calculate_floor(self):
        if type(self.data["input"]) is int:
            return None

        floor = int(self.data["input"])
        if floor != self.data["input"]:
            return floor
        else:
            return None

    def calculate_ceil(self):
        if type(self.data["input"]) is int:
            return None

        if self.data["input"] != int(self.data["input"]):
            return int(self.data["input"]) + 1
        else:
            return None


class PointDatum(Datum):
    def calculate_x(self):
        return self.data["input"][0]

    def calculate_y(self):
        return self.data["input"][1]

    def calculate_z(self):
        if len(self.data["input"]) > 2:
            return self.data["input"][2]
        else:
            return None

class BoundingBoxDatum(Datum):
    def calculate_upper_left(self):
        return self.data["input"][0]
    def calculate_lower_right(self):
        return self.data["input"][1]

    def calculate_width(self):
        return self.data["input"][1][0] - self.data["input"][0][0]
    def calculate_height(self):
        return self.data["input"][1][1] - self.data["input"][0][1]

class ImageDatum(Datum):
    def calculate_blobs(self):
        im = self.data["input"]

        # Set up the detector with default parameters.
        detector = cv2.SimpleBlobDetector_create()

        # Detect blobs.
        keypoints = detector.detect(im)

        return [keypoint.pt for keypoint in keypoints]

    # Calculate the average gray value in the image to determine a "lightness"
    def calculate_lightness(self):
        gray = cv2.cvtColor(self.data["input"], cv2.COLOR_BGR2GRAY)
        return cv2.mean(gray)[0]

    face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')

    def calculate_faces(self):
        gray = cv2.cvtColor(self.data["input"], cv2.COLOR_BGR2GRAY)
        faces = self.__class__.face_cascade.detectMultiScale(gray, 1.3, 5)
        return [(x,y,x+w,y+h) for (x,y,w,h) in faces]

"""
1. Find the last `n` nodes with the same type / value as the passed node
"""
def pattern(node, verbose=False):
    # Step 1: Find the last `n` nodes with the same type / value as the passed node
    number_of_past_nodes_to_find = 5
    past_nodes = []

    pointer = node.prev # start at the node after the current node
    while pointer:
        if type(pointer) == type(node) and pointer.data["input"] == node.data["input"]:
            past_nodes.append(pointer)
            if len(past_nodes) >= number_of_past_nodes_to_find:
                break

        pointer = pointer.prev

    # Step 2: Calculate a fingerprint for the pattern. This is done by roughly "averageing" all
    # values after each node.
    point = []
    weights = []
    for ct, pointer in enumerate(past_nodes):
        if verbose:
            print()
            print( "--START--")

        # Loop through all nodes in between the node indicated by `pointer` and the next value of
        # `pointer`
        index = 0
        while pointer and pointer.prev not in past_nodes:
            if verbose: print( pointer)

            # Has a value this far back from the original `pointer` value been created before? This
            # case is run on the first loop iteration.
            if index > len(point)-1:
                if verbose: print( "  ADD TO END", pointer.data["input"])
                # Add the new point and its weight to the end.
                point.append(pointer)
                weights.append(1)
            else:
                if verbose: print( "  SOMETHING ELSE")
                old_index = index
                while index <= len(point)-1:
                    # On the second loop (outer) iteration, did the node after the `pointer` match?
                    if point[index].data["input"] == pointer.data["input"]:
                        if index <= len(point)-1:
                            # Increment the weight at that node (multiple nodes have it in common)
                            # so that `pointer` effectively votes for this node.
                            weights[index] += 1
                            if verbose: print( "  INCREMENT AT", index)
                        else:
                            point.insert(index, pointer)
                            weights.insert(index, 1)
                            if verbose: print( "  ADD NEW AFTER", index)
                        break

                    index += 1

            index += 1
            pointer = pointer.prev

        if verbose:
            print( "--END--")
            print()

    # Step 3: Finally, average every weight in `weights` so it's within 0 <= n <= 1
    if len(weights) > 0:
        max_weight = float(max(weights))
        weights = [w / max_weight for w in weights]

        return list(zip(point, weights))
    else:
        return []



def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def node_similarity(a, b):
    if type(a) != type(b):
        return 0
    elif a.data["input"] == b.data["input"]:
        return 1
    elif type(a) == TextDatum:
        theoretical_max_difference = len(a.data["input"]) + len(b.data["input"])
        distance = levenshtein(a.data["input"], b.data["input"]) * 1.0

        # The closer `distance` is to `theoretical_max_difference`, the closer this value is to 1
        return (theoretical_max_difference - distance) / theoretical_max_difference
    elif type(a) == NumberDatum:
        value_a = a.data["input"]
        value_b = b.data["input"]

        value_a_threshold = value_a * 0.2 # 20% on either side.

        if value_b > (value_a + value_a_threshold) or value_b < (value_a - value_a_threshold):
            # Outside of threshold. Not a match.
            return 0
        else:
            return 1


def matches_pattern(node, pattern):
    total_score = 0
    max_possible_score = 0

    index = 0
    pointer = node.prev # start at the node after the current node
    while pointer and index < len(pattern):
        total_score += node_similarity(pattern[index][0], pointer) * pattern[index][1]
        max_possible_score += 1
        for i in range(index, len(pattern)):
            total_score += node_similarity(pattern[i][0], pointer) * pattern[i][1]
            max_possible_score += 1

        pointer = pointer.prev
        index += 1

    return total_score / max_possible_score





# ingest("a")
# ingest("b")
#
# ingest("c")
# ingest("bla")
# ingest("a")
# ingest("b")
#
# ingest("bla")
# ingest("z")
# ingest("a")
# ingest("b")
#
# ingest("c")
# ingest("a")
# ingest("b")
ingest(cv2.imread('./images/1-modified.png'))

print()
print()

node = Datum.current_datum
while node:
    print(node)
    node = node.prev

print()
print()

# print( "PATTERN")
# pattern = pattern(Datum.current_datum)
# print( pattern)

# print()
# print( "MATCHES PATTERN")
# print( matches_pattern(Datum.current_datum, pattern))

# print( node_similarity(TextDatum("abcd"), TextDatum("abd")))
