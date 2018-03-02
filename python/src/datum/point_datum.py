from .base_datum import Datum

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
