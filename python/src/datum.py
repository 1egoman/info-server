import cv2
import numpy as np;

MAX_DEPTH = 10

SOURCE_FRAMES = {}

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

    # (ndarray, "source", frame_number)
    elif datumType is FrameDatum:
        img, source, frame_number = data
        node = FrameDatum(img, source, frame_number, SOURCE_FRAMES.get(source), depth=depth, maxdepth=MAX_DEPTH)
        SOURCE_FRAMES[source] = node

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
    # node.calculate()

    # Link node to right side of Datum.current_datum
    node.prev = Datum.current_datum
    if Datum.current_datum:
        Datum.current_datum.next = node
    Datum.current_datum = node


    return node




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
# ingest(cv2.imread('./images/1-modified.png'))
# ingest(cv2.imread('./images/2-modified.png'))
# ingest("a")
# ingest("b")

# print()
# print()
#
# node = Datum.current_datum
# while node:
#     print(node)
#     node = node.prev
#
# print()
# print()

# print( "PATTERN")
# pattern = pattern(Datum.current_datum)
# print( pattern)
#
# print()
# print( "MATCHES PATTERN")
# print( matches_pattern(Datum.current_datum, pattern))

# print( node_similarity(TextDatum("abcd"), TextDatum("abd")))





model = [
    # What I want:
    # ([[TextDatum('a'), TextDatum('d'), TextDatum('c'), TextDatum('b')]], TextDatum('b')),
    # ([[TextDatum('b'), TextDatum('a'), TextDatum('d'), TextDatum('c')]], TextDatum('c')),
    # ([[TextDatum('c'), TextDatum('b'), TextDatum('a'), TextDatum('d')]], TextDatum('d')),
    # ([[TextDatum('d'), TextDatum('c'), TextDatum('b'), TextDatum('a')]], TextDatum('a')),
]

def add_to_model(node):
    pattern = []

    pointer = node.prev
    for i in range(0, 4):
        pattern.append(pointer)
        pointer = pointer.prev

    model.append(([pattern], node))

ingest("foo")
ingest(1)
ingest("hello")
ingest(1)

ingest("foo")
add_to_model(Datum.current_datum)
ingest(1)
add_to_model(Datum.current_datum)
ingest("hello")
add_to_model(Datum.current_datum)
ingest(1)
add_to_model(Datum.current_datum)

ingest("foo")
add_to_model(Datum.current_datum)
ingest(1)
add_to_model(Datum.current_datum)

# Write a function that takes [NumberDatum(1), NumberDatum(2)] and determines if NumberDatum(2.5) is
# similar to all nodes in the set.

def predict_next(last):
    result = []
    all_totals = 0

    # Loop through each classification in the model
    for row in model:
        total = 0
        # Loop through each possibility within the classification
        for items in row[0]:
            # If items is [NumberDatum(1)] for example, then:
            #     total += node_similarity(items[0], last) * (10/10)
            # If items is [NumberDatum(1), NumberDatum(2)] for example, then:
            #     total += node_similarity(items[0], last) * (10/10) + node_similarity(items[1], last.prev) * (9/10)
            # If items is [NumberDatum(1), NumberDatum(2), NumberDatum(3)] for example, then:
            #     total += node_similarity(items[0], last) * (10/10) + node_similarity(items[1], last.prev) * (9/10) + node_similarity(items[2], last.prev.prev) * (8/10)
            # and so on...

            node = last
            for ct, item in enumerate(items):
                history_weight = (10 - ct) / 10
                total += node_similarity(item, node) * history_weight #* (1 / len(items))
                node = node.prev

        all_totals += total
        result.append((row[1], total))

    if all_totals > 0:
        return [(label, total / all_totals) for (label, total) in result]
    else:
        return result

# a = NumberDatum(2)
# b = NumberDatum(2)
# a.prev = b
#
print(predict_next(Datum.current_datum))
print()
for line in model:
    print(line)
