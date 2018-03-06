from datum import TextDatum, NumberDatum

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


def diff(a, b):
    last_match_index = 0
    best_probabilities_for_place = [(0, 0) for _ in a]

    for index_a, item_a in enumerate(a):
        for index_b, item_b in enumerate(b):

            # Rough similarity metric
            # replace with `value = node_similarity(item_a, item_b)`
            # value = abs(1 - (abs(item_a - item_b) * 0.1)) if abs(item_a - item_b) > 0 else 1.0
            value = node_similarity(item_a, item_b)

            # If the current comparison of item_a and item_b is greater than the current value for
            # item_a and item_b, and the item is after the last match (ie, to ensure that the order
            # in matches is preserved), then update the best probabilities with the current value.
            if (
                value > best_probabilities_for_place[index_a][1] and \
                index_b >= best_probabilities_for_place[index_a-1][0]
            ):
                best_probabilities_for_place[index_a] = (index_b, value)

    # Pick the item with the largest value for a given index. TODO
    # [(1, 1.0), (1, 0.9), (3, 1.0), (3, 0.9), (3, 0.8), (4, 0.8), (4, 0.9), (4, 1.0)]
    #    /\                   /\                                                /\

    matches = [(-1, 0) for _ in a]
    for index, item in enumerate(best_probabilities_for_place):
        if item[1] > matches[index][1]:
            matches[index] = item


    return [(index, match[0], match[1]) for index, match in enumerate(matches) if match[0] != -1]

def extract_similar_regions(pointer):
    head = pointer
    pointer = pointer.prev

    similar_heads = []

    while pointer:
        if node_similarity(head, pointer) > 0.8:
            similar_heads.append(pointer)

        pointer = pointer.prev

# result = diff(
#     # [1, 2,  3, 4,  5],
#     # [2, 10, 4, 14, 8],
#
#     # [1, 2, 3, 4, 5],
#     # [2, 5, 4, 14, 8],
#
#     [1, 2, 3, 4, 5, 6, 7, 8],
#     [4, 1, 6, 3, 8],
# )
