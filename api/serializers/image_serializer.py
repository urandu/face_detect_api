from rest_framework import serializers

from apps.api.models.image import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta():
        model = Image
        fields = ('file', 'image_id', 'callback_url', 'date_created')