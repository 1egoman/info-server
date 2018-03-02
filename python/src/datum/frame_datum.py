from .image_datum import ImageDatum


class FrameDatum(ImageDatum):
    def __init__(self, seed_data, source, frame_number, last_frame, **kwargs):
        super(ImageDatum, self).__init__(seed_data, **kwargs)

        self.source = source
        self.data["frame_number"] = frame_number
        self.last_frame = last_frame

    def calculate(self):
        for i in dir(self):
            if i.startswith("calculate_"):
                # Set the attribute on the Datum
                value = getattr(self, i)()
                if value is None: continue
                key = i[len("calculate_"):]
                self.data[key] = value

                # Add a new Datum, ensuring that we only recurse so deep and that duplicates should
                # be avoided.
                if (
                    self.maxdepth and self.depth + 1 < self.maxdepth
                ) and (
                    type(self.data["input"]) is np.ndarray or self.data["input"] != value
                ):
                    if type(value) is list:
                        # Ingest an array of values one at a time
                        for ct, v in enumerate(value):
                            ingest(v, depth=self.depth+1)
                            ingest(last_frame.data[key][ct] - v, depth=self.depth+1)
                    else:
                        # Ingest a single value
                        ingest(value, depth=self.depth+1)
                        ingest(last_frame.data[key] - value, depth=self.depth+1)

