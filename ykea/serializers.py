from .models import Item
from rest_framework import serializers

class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Item
        fields = (
        'url', 'item_number', 'name', 'description', 'price',
        'is_new', 'size', 'instructions', 'featured_photo',
        'category')



