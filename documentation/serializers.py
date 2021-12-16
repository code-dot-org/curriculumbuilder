import json
from rest_framework import serializers
from documentation.models import Map

class MapExportSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Map
        fields = ('title', 'content', 'slug', 'category', 'children')

    def get_category(self, obj):
        return obj.get_absolute_url()

    def get_children(self, obj):
        return obj.get_children().map(lambda map: map.name)
