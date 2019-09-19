# The future is now!
import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
import os

from django.conf import settings


def upload_image(request):
    img = request.FILES['image']
    img_extension = os.path.splitext(img.name)[-1]
    # return path to saved image
    return default_storage.save(settings.MEDIA_URL + str(uuid.uuid4()) + img_extension, img)
#
# def detect_faces(self, image_id, required_size=(160, 160), classify_faces=False):
#     image_object = Image_object.objects.get(image_id=image_id)
#     filename = image_object.name
#     image = Image.open(default_storage.open(filename))
#     image = image.convert('RGB')
#     pixels = asarray(image)
#
#     detector = MTCNN()
#     # detect faces in the image
#
#     results = detector.detect_faces(pixels)
#
#     # extract the bounding box from the first face
#     detected_faces = list()
#     for result in results:
#
#         # only detect faces with a confidence of 90% and above
#         if result['confidence'] > 0.94:
#             face_object = Face()
#             face_id = str(uuid.uuid4())
#             face_object.face_id = face_id
#             face_object.image_id = image_id
#             face_object.confidence = result['confidence']
#             face_object.box = result['box']
#             face_object.keypoints = result['keypoints']
#             face_object.save()
#             # do not queue tasks if its a classification workflow
#             if not classify_faces:
#                 chain(
#                     create_face_array.s(face_id) |
#                     embed_face.s(face_id=face_id)| encode_face.s(face_id=face_id)
#                 ).delay()
#
#             detected_faces.append(face_id)
#
#     # check of faces were detected, if faces were detected, schedule face embedding tasks as group else, schedule callback task
#     if classify_faces:
#         if detected_faces:
#             chord([(create_face_array.s(face_id=i) | embed_face.s(face_id=i) | encode_face.s(face_id=i)| classify_face.s(face_id=i)) for i in
#                    detected_faces])(classify_image_callback.s(image_id=image_id))
#
#     return detected_faces



class Image(APIView):

    def post(self, request, *args, **kwargs):

        upload = upload_image(request=request)

        return Response({"success":upload}, status=status.HTTP_202_ACCEPTED)


