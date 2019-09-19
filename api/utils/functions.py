# The future is now!
from django.core.files.storage import default_storage
import os
from django.conf import settings
import uuid


def upload_image(self, request):
    img = request.FILES['image']
    img_extension = os.path.splitext(img.name)[-1]
    default_storage.save(settings.MEDIA_URL + str(uuid.uuid4()) + img_extension, img)

