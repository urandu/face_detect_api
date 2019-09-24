# The future is now!
import uuid
from django.core.files.storage import default_storage
from mtcnn.mtcnn import MTCNN
from numpy import asarray
from api.models.face import Face
from api.models.image import Image as Image_object
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



@app.task(bind=True, name='detect_faces_callback')
def detect_faces_callback(self, *args, **kwargs):
    image_id = kwargs.get("image_id")
    image_object = Image_object.objects.get(image_id=image_id)

    filename = image_object.name
    output_filename = "detected_faces/" + image_object.name
    faces_on_image = Face.objects.filter(image_id=image_id)
    image = PImage.open(default_storage.open(filename))
    image = np.array(image)
    # image = cv2.imread(default_storage.open(filename))
    image = image.copy()
    for face in faces_on_image:
        classification = Classification.objects.get(face_id=face.face_id)
        box = json.loads(face.box)

        x1, y1, width, height = box
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 5)
        cv2.putText(image,
                    "P: " + "{0:.4f}".format(float(classification.probability)) + " ID:" + classification.cluster_id[
                                                                                           :7],
                    (x1, (y2 + 25)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

    # cv2_im = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(image)
    silver_bullet = io.BytesIO()
    pil_im.save(silver_bullet, format="JPEG")

    image_file = InMemoryUploadedFile(silver_bullet, None, "nnnn.jpg", 'image/jpeg',
                                      len(silver_bullet.getvalue()), None)

    default_storage.save(output_filename, image_file)
    # pil_im.save(default_storage.save(output_filename))
    # cv2.imwrite(output_filename,
    #             image)

    return kwargs.get("image_id", "piladi ID returned because image ID missing")
