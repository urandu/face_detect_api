# The future is now!
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from api.models.image import Image as Image_object
from api.serializers.image_serializer import ImageSerializer
from api.tasks.image import detect_faces
import os
from minio import Minio
from minio.error import ResponseError
from django.conf import settings


def upload_image(request, image_id):

    # check if minio bucket exists
    minioClient = Minio(settings.MINIO_STORAGE_ENDPOINT,
                        access_key=settings.MINIO_STORAGE_ACCESS_KEY,
                        secret_key=settings.MINIO_STORAGE_SECRET_KEY,
                        secure=False)
    try:
        minioClient.bucket_exists(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME)
    except ResponseError as err:
        # log then create bucket
        minioClient.make_bucket(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME)



    img = request.FILES['image']
    img_extension = os.path.splitext(img.name)[-1]
    return default_storage.save(image_id + img_extension, request.FILES['image'])


class Image(APIView):


    def post(self, request, *args, **kw):
        image_serializer = ImageSerializer(data=request.data)
        if image_serializer.is_valid():
            image_id = request.data.get("image_id")
            callback_url = request.data.get("callback_url")
            name = upload_image(request, image_id)
            image = Image_object()
            image.image_id = image_id
            image.callback_url = callback_url
            image.name = name
            image.save()

            detect_faces.s(image_id=image_id).delay()

            return Response({"status":"ok"}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)