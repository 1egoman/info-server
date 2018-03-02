from .base_datum import Datum

class BoundingBoxDatum(Datum):
    def calculate_upper_left(self):
        return self.data["input"][0]
    def calculate_lower_right(self):
        return self.data["input"][1]

    def calculate_width(self):
        return self.data["input"][1][0] - self.data["input"][0][0]
    def calculate_height(self):
        return self.data["input"][1][1] - self.data["input"][0][1]
