import requests
import cv2

from PIL import Image

import spacy
nlp = spacy.load('en')
def stemmer(word):
    return nlp(word)[0].lemma_

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
            im = Image.open(r.raw)

            # If image has transpareny, remove it.
            if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

                # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
                alpha = im.convert('RGBA').split()[-1]

                # Create a new background image of our matt color.
                # Must be RGBA because paste requires both images have the same format
                # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
                bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
                bg.paste(im, mask=alpha)
                im = bg

            im = im.convert('RGB')

            print("  ... Size:", im.size)

            # Save, but in a lower quality and compressed
            im.save('/tmp/image.jpeg', 'JPEG', quality=2)

            # Add the image to the pipeline
            pipeline = Pipeline()
            image_datum = ingest(cv2.imread('/tmp/image.jpeg'), pipeline=pipeline)
            # pipeline.debug()

            # Add the pipeline as metadata
            concept.add_metadata(METADATA["RELATED_IMAGE"], pipeline)
            print("  ... Added RELATED_IMAGE for", phrase)
