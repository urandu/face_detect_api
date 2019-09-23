# The future is now!
import uuid

from django.core.files.storage import default_storage
import os
from mtcnn.mtcnn import MTCNN
from numpy import asarray
from PIL import Image as PImage

from django.conf import settings


def detect_faces(image_path):

    image = PImage.open(default_storage.open(image_path))
    image = image.convert('RGB')
    pixels = asarray(image)

    detector = MTCNN()
    # detect faces in the image

    results = detector.detect_faces(pixels)

    # extract the bounding box from the faces
    detected_faces = list()
    for result in results:

        # only detect faces with a confidence of 90% and above
        if result['confidence'] > 0.90:
            detected_faces.append({
                "face_id":uuid.uuid4(),
                "confidence": result['confidence'],
                "bounding_box": result['box'],
                "keypoints":result['keypoints']
            })

    return detected_faces
