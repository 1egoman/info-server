from .base_datum import Datum

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
