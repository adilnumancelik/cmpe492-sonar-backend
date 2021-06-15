from django.db import models
from django.db.models import fields
from api.models import *
from rest_framework import serializers, status
import json


class DummySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dummy
        fields = ['name', 'value']

class NodeGetSerializer(serializers.ModelSerializer):
    specific_information = serializers.SerializerMethodField('get_specific_info')
    class Meta: 
        model = Node
        fields = '__all__'
    
    def get_specific_info(self, obj):
        return json.loads(obj.specific_information)
        #return obj.specific_information


class NodeSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Node
        fields = '__all__'
    

class EdgeSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Edge
        fields = '__all__'

class EdgeGetSerializer(serializers.ModelSerializer):
    specific_information = serializers.SerializerMethodField('get_specific_info')
    class Meta: 
        model = Edge
        fields = '__all__'

    def get_specific_info(self, obj):
        return json.loads(obj.specific_information)
        #return obj.specific_information


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
            data.append(NodeGetSerializer(node).data)
        return data
    
    def get_edges(self, obj):
        data = []
        for edge in obj['edges']:
            data.append(EdgeGetSerializer(edge).data)
        return data

    def get_status(self, obj):
        is_successful = self.context.get('is_successful')
        message = self.context.get('message')
        return {
            'successful': is_successful,
            'message': message
        }



class ArticleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField('get_title')
    class Meta:
        model = Article
        fields = '__all__'

    def get_title(self, obj):
        if obj.title == "":
            return None
        
        return obj.title


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
