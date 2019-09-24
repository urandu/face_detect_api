# The future is now!
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from api.models.image import Image as Image_object
from api.tasks.image import detect_faces
import os
from minio import Minio
from django.conf import settings


def upload_image(request, image_id):

    # check if minio bucket exists
    minioClient = Minio(settings.MINIO_STORAGE_ENDPOINT,
                        access_key=settings.MINIO_STORAGE_ACCESS_KEY,
                        secret_key=settings.MINIO_STORAGE_SECRET_KEY,
                        secure=False)
    try:
        print(minioClient.bucket_exists(settings.MINIO_STORAGE_SECRET_KEY))
    except ResponseError as err:
        print(err)


    img = request.FILES['image']
    img_extension = os.path.splitext(img.name)[-1]
    return default_storage.save(image_id + img_extension, request.FILES['image'])


class Image(APIView):

    def post(self, request, *args, **kwargs):
        image_id = str(uuid.uuid4())
        name = upload_image(request, image_id)
        image = Image_object()
        image.image_id = image_id
        image.name = name
        image.save()

        detect_faces.s(image_id=image_id).delay()

        return Response({"status":"ok"}, status=status.HTTP_202_ACCEPTED)