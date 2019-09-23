# The future is now!
import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
import os
from mtcnn.mtcnn import MTCNN
from numpy import asarray
from PIL import Image as PImage

from django.conf import settings


def upload_image(request, image_id):
    img = request.FILES['file']
    img_extension = os.path.splitext(img.name)[-1]
    return default_storage.save(image_id + img_extension, request.FILES['file'])

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



class Image(APIView):

    def post(self, request, *args, **kwargs):
        image_id = str(uuid.uuid4())
        name = upload_image(request, image_id)
        image = Image()
        image.image_id = image_id
        image.name = name
        image.save()

        return Response({"status":"ok"}, status=status.HTTP_202_ACCEPTED)


