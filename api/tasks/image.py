# The future is now!
import uuid

import requests
from django.core.files.storage import default_storage
from mtcnn.mtcnn import MTCNN
from numpy import asarray
from api.models.face import Face
from api.models.image import Image as Image_object
from PIL import Image as PImage, ImageOps
from api.celery_app import app
import numpy as np
import json
import cv2
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

# Face detection configuration
FACE_CONFIDENCE_THRESHOLD = 0.94
IOU_THRESHOLD = 0.5


def transform_box_coordinates(box, keypoints, angle, image_width, image_height):
    """
    Transform bounding box and keypoints coordinates back to original orientation.
    
    Args:
        box: [x, y, width, height] in rotated image
        keypoints: dict with 'left_eye', 'right_eye', 'nose', 'mouth_left', 'mouth_right'
        angle: rotation angle (0, 90, 180, 270)
        image_width: original image width
        image_height: original image height
    
    Returns:
        transformed box and keypoints
    """
    x, y, width, height = box
    
    if angle == 0:
        return box, keypoints
    elif angle == 90:
        # 90 degrees clockwise: (x, y) -> (y, width - x - box_width)
        new_x = y
        new_y = image_width - x - width
        new_width = height
        new_height = width
        new_keypoints = {}
        for key, (kx, ky) in keypoints.items():
            new_keypoints[key] = (ky, image_width - kx)
        return [new_x, new_y, new_width, new_height], new_keypoints
    elif angle == 180:
        # 180 degrees: (x, y) -> (width - x - box_width, height - y - box_height)
        new_x = image_width - x - width
        new_y = image_height - y - height
        new_keypoints = {}
        for key, (kx, ky) in keypoints.items():
            new_keypoints[key] = (image_width - kx, image_height - ky)
        return [new_x, new_y, width, height], new_keypoints
    elif angle == 270:
        # 270 degrees clockwise: (x, y) -> (height - y - box_height, x)
        new_x = image_height - y - height
        new_y = x
        new_width = height
        new_height = width
        new_keypoints = {}
        for key, (kx, ky) in keypoints.items():
            new_keypoints[key] = (image_height - ky, kx)
        return [new_x, new_y, new_width, new_height], new_keypoints
    
    return box, keypoints


@app.task(bind=True, name='detect_faces')
def detect_faces(self, *args, **kwargs):
    image_id = kwargs.get("image_id")
    image_object = Image_object.objects.get(image_id=image_id)
    filename = image_object.name
    image = PImage.open(default_storage.open(filename))
    
    # Correct image orientation based on EXIF data
    image = ImageOps.exif_transpose(image)
    
    image = image.convert('RGB')
    
    # Store original dimensions
    original_width, original_height = image.size
    
    detector = MTCNN()
    
    # Try different orientations to detect faces
    rotations = [0, 90, 180, 270]
    all_results = []
    
    for angle in rotations:
        # Rotate image
        if angle == 0:
            rotated_image = image
        else:
            rotated_image = image.rotate(-angle, expand=True)
        
        pixels = asarray(rotated_image)
        
        # Get current image dimensions (may change after rotation)
        current_width, current_height = rotated_image.size
        
        # detect faces in the rotated image
        results = detector.detect_faces(pixels)
        
        # Transform coordinates back to original orientation
        for result in results:
            if result['confidence'] > FACE_CONFIDENCE_THRESHOLD:
                # Transform box and keypoints back to original orientation
                transformed_box, transformed_keypoints = transform_box_coordinates(
                    result['box'],
                    result['keypoints'],
                    angle,
                    original_width,
                    original_height
                )
                
                # Add to results with transformed coordinates
                all_results.append({
                    'box': transformed_box,
                    'keypoints': transformed_keypoints,
                    'confidence': result['confidence'],
                    'angle': angle
                })

    # Remove duplicate detections (faces detected in multiple orientations)
    # Keep the one with highest confidence
    unique_results = []
    for result in all_results:
        # Check if this is a duplicate of an existing detection
        is_duplicate = False
        duplicate_index = -1
        for i, unique_result in enumerate(unique_results):
            # Calculate overlap between bounding boxes
            box1 = result['box']
            box2 = unique_result['box']
            
            x1_min, y1_min = box1[0], box1[1]
            x1_max, y1_max = x1_min + box1[2], y1_min + box1[3]
            x2_min, y2_min = box2[0], box2[1]
            x2_max, y2_max = x2_min + box2[2], y2_min + box2[3]
            
            # Calculate intersection
            x_overlap = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
            y_overlap = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
            intersection = x_overlap * y_overlap
            
            # Calculate union
            area1 = box1[2] * box1[3]
            area2 = box2[2] * box2[3]
            union = area1 + area2 - intersection
            
            # If IoU (Intersection over Union) > threshold, consider as duplicate
            if union > 0 and intersection / union > IOU_THRESHOLD:
                is_duplicate = True
                duplicate_index = i
                # Keep the one with higher confidence
                if result['confidence'] > unique_result['confidence']:
                    break
                else:
                    # Current result has lower confidence, skip it
                    break
        
        if is_duplicate and duplicate_index >= 0 and result['confidence'] > unique_results[duplicate_index]['confidence']:
            # Replace with higher confidence detection
            unique_results[duplicate_index] = result
        elif not is_duplicate:
            unique_results.append(result)

    detected_faces = list()
    for result in unique_results:
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
    
    # Correct image orientation based on EXIF data
    image = ImageOps.exif_transpose(image)
    
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
    image_object.status = "completed"
    image_object.save()

    try:
        requests.post(url=image_object.callback_url, data=json.dumps(callback))
    except Exception as e:
        # log exception
        pass

    return image_id
