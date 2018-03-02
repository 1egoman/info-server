from .base_datum import Datum

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
