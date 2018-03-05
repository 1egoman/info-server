import cv2
from .base_datum import Datum


class ImageDatum(Datum):
    def calculate_blobs(self):
        print("CALCULATING BLOBS")
        im = self.data["input"]

        # Set up the detector with default parameters.
        detector = cv2.SimpleBlobDetector_create()

        # Detect blobs.
        keypoints = detector.detect(im)

        return [keypoint.pt for keypoint in keypoints]

    # Calculate the average gray value in the image to determine a "lightness"
    def calculate_lightness(self):
        gray = cv2.cvtColor(self.data["input"], cv2.COLOR_BGR2GRAY)
        return cv2.mean(gray)[0]

    face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')

    def calculate_faces(self):
        gray = cv2.cvtColor(self.data["input"], cv2.COLOR_BGR2GRAY)
        faces = self.__class__.face_cascade.detectMultiScale(gray, 1.3, 5)
        return [(x,y,x+w,y+h) for (x,y,w,h) in faces]
