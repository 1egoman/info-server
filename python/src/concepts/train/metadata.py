import requests
import cv2

from PIL import Image

from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()

from ...datum import Pipeline, ImageDatum
from ...datum.ingest import ingest
from ..concept import Concept
from ..metadata import METADATA

BASE_URL = "https://api.qwant.com/api/search/images?count=10&offset=1&q={}"

def train(phrase):
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

            # Add the image to the pipeline
            pipeline = Pipeline()
            image_datum = ingest(cv2.imread('/tmp/image.jpeg'), pipeline=pipeline)
            pipeline.debug()

            # Add the pipeline as metadata
            concept.add_metadata(METADATA["RELATED_IMAGE"], pipeline)
            print("  ... Added RELATED_IMAGE for", phrase)
