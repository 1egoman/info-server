import numpy as np
MAX_DEPTH = 10

from .base_datum import Datum, Pipeline
from .bounding_box_datum import BoundingBoxDatum
from .frame_datum import FrameDatum
from .image_datum import ImageDatum
from .number_datum import NumberDatum
from .point_datum import PointDatum
from .text_datum import TextDatum

def ingest(data, depth=0, pipeline=Datum.default_pipeline, datumType=None):

    datumType = type(data)

    # Figure out how to ingest the data
    node = None
    # "Hello World"
    if datumType is str:
        node = TextDatum(data, depth=depth, maxdepth=MAX_DEPTH, pipeline=pipeline)

    # 5 or 3.28
    elif datumType is int or datumType is float:
        node = NumberDatum(data, depth=depth, maxdepth=MAX_DEPTH, pipeline=pipeline)

    # (ndarray, "source", frame_number)
    elif datumType is FrameDatum:
        img, source, frame_number = data
        node = FrameDatum(img, source, frame_number, SOURCE_FRAMES.get(source), depth=depth, maxdepth=MAX_DEPTH, pipeline=pipeline)
        SOURCE_FRAMES[source] = node

    # ((1, 1), (2, 2))
    elif datumType is tuple and len(data) in [2, 3] and type(data[0]) is tuple:
        node = PointDatum(data, depth=depth, maxdepth=MAX_DEPTH, pipeline=pipeline)

    # (1, 1)
    elif datumType is tuple and len(data) in [2, 3]:
        node = PointDatum(data, depth=depth, maxdepth=MAX_DEPTH, pipeline=pipeline)

    elif datumType is np.ndarray and len(data.shape) == 3:
        node = ImageDatum(data, depth=depth, maxdepth=MAX_DEPTH, pipeline=pipeline)

    else:
        raise Exception("Dont know which datum type to make!")

    # Derive other properties of the node. Add them to the pipeline before the current node.
    node.calculate()

    # Link node to right side of Datum.current_datum
    node.prev = pipeline.current_datum
    if pipeline.current_datum:
        pipeline.current_datum.next = node
    pipeline.current_datum = node

    return node
