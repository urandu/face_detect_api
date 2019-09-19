# The future is now!
import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
import os
from mtcnn.mtcnn import MTCNN
from numpy import asarray

from django.conf import settings


def upload_image(request):
    img = request.FILES['image']
    img_extension = os.path.splitext(img.name)[-1]
    # return path to saved image
    return default_storage.save(settings.MEDIA_URL + str(uuid.uuid4()) + img_extension, img)

def detect_faces(image_path):

    image = Image.open(default_storage.open(image_path))
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

        upload = upload_image(request=request)
        detected_faces = detect_faces(upload)
        return Response({"success":detected_faces}, status=status.HTTP_202_ACCEPTED)


