# The future is now!
import uuid
from django.core.files.storage import default_storage
from mtcnn.mtcnn import MTCNN
from numpy import asarray
from api.models.face import Face
from ..models.image import Image as Image_object
from PIL import Image as PImage
from api.celery_app import app


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
