from django.db import models
from django.db.models import fields
from api.models import *
from rest_framework import serializers, status
import json


class DummySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dummy
        fields = ['name', 'value']

class NodeSerializer(serializers.ModelSerializer):
    specific_information = serializers.SerializerMethodField('get_specific_info')
    class Meta: 
        model = Node
        fields = '__all__'

    def get_specific_info(self, obj):
        #return json.loads(obj.specific_information)
        return obj.specific_information

class EdgeSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Edge
        fields = '__all__'


class GraphSerializer(serializers.ModelSerializer):
    nodes = serializers.SerializerMethodField('get_nodes')
    edges = serializers.SerializerMethodField('get_edges')
    status = serializers.SerializerMethodField('get_status')

    class Meta:
        model = Node
        fields = ('nodes', 'edges', 'status')

    def get_nodes(self, obj):
        data = []
        for node in obj['nodes']:
            data.append(NodeSerializer(node).data)
        return data
    
    def get_edges(self, obj):
        data = []
        for edge in obj['edges']:
            data.append(EdgeSerializer(edge).data)
        return data

    def get_status(self, obj):
        is_successful = self.context.get('is_successful')
        message = self.context.get('message')
        return {
            'successful': is_successful,
            'message': message
        }



class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class ArticleListItemsResponseSerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField('get_result')
    status = serializers.SerializerMethodField('get_status')
    
    class Meta:
        model = Article
        fields = ('result', 'status')

    def get_result(self, obj):
        data = []
        for article in obj:
            data.append(ArticleSerializer(article).data)
        return data

    def get_status(self, obj):
        is_successful = self.context.get('is_successful')
        message = self.context.get('message')
        return {
            'successful': is_successful,
            'message': message
        }

class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleList
        fields = '__all__'

class ArticleListResponseSerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField('get_result')
    status = serializers.SerializerMethodField('get_status')
    
    class Meta:
        model = ArticleList
        fields = ('result', 'status')

    def get_result(self, obj):
        data = []
        for list in obj:
            data.append(ArticleListSerializer(list).data)
        return data

    def get_status(self, obj):
        is_successful = self.context.get('is_successful')
        message = self.context.get('message')
        return {
            'successful': is_successful,
            'message': message
        }

class ArticleListToDOISerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleListToDOI
        fields = '__all__'