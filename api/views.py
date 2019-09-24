# The future is now!
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from api.tasks.image import detect_faces
import os


def upload_image(request, image_id):
    img = request.FILES['file']
    img_extension = os.path.splitext(img.name)[-1]
    return default_storage.save(image_id + img_extension, request.FILES['file'])


class Image(APIView):

    def post(self, request, *args, **kwargs):
        image_id = str(uuid.uuid4())
        name = upload_image(request, image_id)
        image = Image()
        image.image_id = image_id
        image.name = name
        image.save()

        detect_faces.s(image_id=image_id).delay()

        return Response({"status":"ok"}, status=status.HTTP_202_ACCEPTED)