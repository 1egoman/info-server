import requests
import cv2

from PIL import Image

from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()

from ...datum import ImageDatum
from ..concept import Concept

BASE_URL = "https://api.qwant.com/api/search/images?count=10&offset=1&q={}"

def train(phrase):
    print("PHRASE", phrase)
    concept = Concept.find(phrase)
    if concept is None:
        return None

    response = requests.get(BASE_URL.format(phrase), headers={
        # Doesn't work with a non-browser user agent :(
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'
    })

    if response.ok:
        json = response.json()
        images = json["data"]["result"]["items"]

        for image in images:
            if len(image["size"]) > 6:
                print("  (skipping image {}, too big)".format(image["media"]))
                continue

            print("  ... Downloading", image["media"])
            image_url = image["media"]

            r = requests.get(image_url, stream=True)
            r.raw.decode_content = True # handle spurious Content-Encoding
            im = Image.open(r.raw).convert('RGB')

            print("  ... Size:", im.size)

            # Save, but in a lower quality and compressed
            im.save('/tmp/image.jpeg', 'JPEG', quality=2)

            image_datum = ImageDatum(cv2.imread('/tmp/image.jpeg'))
            image_datum.calculate()
            print(image_datum)

        # Image.open('/tmp/image.jpeg').show()
