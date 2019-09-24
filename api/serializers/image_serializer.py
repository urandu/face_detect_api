from rest_framework import serializers

from api.models.image import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta():
        model = Image
        fields = ('image', 'image_id', 'callback_url', 'date_created')