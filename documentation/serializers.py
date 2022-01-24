import json
from rest_framework import serializers
from documentation.models import Block, Example, Map, Parameter

class MapExportSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()

    class Meta:
        model = Map
        fields = ('title', 'content', 'slug', 'order', 'children')

    def get_children(self, obj):
        return map(lambda x: x.slug, obj.get_children())
        
    def get_order(self, obj):
        return obj._order

class ParameterExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('name', 'type', 'required', 'description')

class ExampleExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Example
        fields = ('name', 'description', 'code', 'app', 'image', 'app_display_type', 'embed_app_with_code_height')

class BlockExportSerializer(serializers.ModelSerializer):
    parameters = serializers.SerializerMethodField()
    examples = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = ('title', 'ext_doc', 'return_value', 'tips', 'video', 'image', 'content', 'description', 'category', 'parameters', 'examples')

    def get_category(self, obj):
        if obj.parent_cat:
            return obj.parent_cat.name
        return None

    def get_parameters(self, obj):
        parameters = obj.parameters.all()
        serializer = ParameterExportSerializer(parameters, many=True, context=self.context)
        return serializer.data

    def get_examples(self, obj):
        examples = obj.examples.all()
        serializer = ExampleExportSerializer(examples, many=True, context=self.context)
        return serializer.data
