import cv2
from .base_datum import Datum


class ImageDatum(Datum):
    def calculate_blobs(self):
        im = self.data["input"]

        params = cv2.SimpleBlobDetector_Params()

        # Change thresholds
        params.minThreshold = 0
        params.maxThreshold = 256

        # Set up the detector with default parameters.
        detector = cv2.SimpleBlobDetector_create(params)

        # Detect blobs.
        keypoints = detector.detect(im)

        def generate_datums(keypoint):
            x = int(keypoint.pt[0])
            y = int(keypoint.pt[1])
            size = int(keypoint.size)

            # Only care about blobs that are decently big.
            if len(im) > 10 and size > 10:
                return [
                    # First, the point representing the blob location.
                    keypoint.pt,
                    # Then, the subimage cropped to only contain the area detected as part of the blob.
                    ImageDatum(im[x:x+size, y:y+size]),
                ]
            else:
                return []

        datums = [generate_datums(keypoint) for keypoint in keypoints]

        if len(im) > 0:
            keyp = cv2.drawKeypoints(im, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            cv2.imshow('Window', keyp)
            cv2.waitKey(0)

        flat_list = [item for sublist in datums for item in sublist]
        return flat_list

    def calculate_width(self):
        return len(self.data["input"])

    def calculate_height(self):
        if len(self.data["input"]) > 0:
            return len(self.data["input"][0])
        else:
            return 0

    # Calculate the average gray value in the image to determine a "lightness"
    def calculate_lightness(self):
        gray = cv2.cvtColor(self.data["input"], cv2.COLOR_BGR2GRAY)
        return cv2.mean(gray)[0]
