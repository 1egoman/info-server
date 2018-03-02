from datum import Datum, BoundingBoxDatum, FrameDatum, \
        ImageDatum, NumberDatum, PointDatum, TextDatum

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
