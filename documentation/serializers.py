import json
from rest_framework import serializers
from documentation.models import Map

class MapExportSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Map
        fields = ('title', 'content', 'slug', 'children')

    def get_children(self, obj):
        return map(lambda x: x.slug, obj.get_children())
