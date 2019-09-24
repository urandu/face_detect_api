# The future is now!
import uuid

import requests
from django.core.files.storage import default_storage
from mtcnn.mtcnn import MTCNN
from numpy import asarray
from api.models.face import Face
from api.models.image import Image as Image_object
from PIL import Image as PImage
from api.celery_app import app
import numpy as np
import json
import cv2
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings


@app.task(bind=True, name='detect_faces')
def detect_faces(self, *args, **kwargs):
    image_id = kwargs.get("image_id")
    image_object = Image_object.objects.get(image_id=image_id)
    filename = image_object.name
    image = PImage.open(default_storage.open(filename))
    image = image.convert('RGB')
    pixels = asarray(image)

    detector = MTCNN()

    # detect faces in the image
    results = detector.detect_faces(pixels)

    detected_faces = list()
    for result in results:

        # only detect faces with a confidence of 94% and above
        if result['confidence'] > 0.94:
            face_object = Face()
            face_id = str(uuid.uuid4())
            face_object.face_id = face_id
            face_object.image_id = image_id
            face_object.confidence = result['confidence']
            face_object.box = result['box']
            face_object.keypoints = result['keypoints']
            face_object.save()
            detected_faces.append(face_id)

    return detected_faces



@app.task(bind=True, name='detect_faces_callback')
def detect_faces_callback(self, *args, **kwargs):
    image_id = kwargs.get("image_id")
    image_object = Image_object.objects.get(image_id=image_id)

    filename = image_object.name
    output_filename = "detected_faces/" + image_object.name
    faces_on_image = Face.objects.filter(image_id=image_id)
    image = PImage.open(default_storage.open(filename))
    image = np.array(image)
    image = image.copy()
    faces_dict = list()
    for face in faces_on_image:
        faces_dict.append({
            "confidence":face.confidence,
            "box":face.box,
            "keypoints":face.keypoints
        })
        box = json.loads(face.box)

        x1, y1, width, height = box
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 5)
        cv2.putText(image,
                    "P: " + "{0:.4f}".format(float(face.confidence)),
                    (x1, (y2 + 25)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

    pil_im = PImage.fromarray(image)
    silver_bullet = io.BytesIO()
    pil_im.save(silver_bullet, format="JPEG")

    image_file = InMemoryUploadedFile(silver_bullet, None, output_filename, 'image/jpeg',
                                      len(silver_bullet.getvalue()), None)

    default_storage.save(output_filename, image_file)

    callback = dict({
        "image_id":image_id,
        "request_id":image_object.request_id,
        "faces":faces_dict,
        "output_image_url":"{host}/api/image/?image_id={image_id}".format(host=settings.API_HOST, image_id=image_id)
    })
    try:
        requests.post(url=image_object.callback_url, data=json.dumps(callback))
    except Exception as e:
        # log exception
        pass

    return image_id
