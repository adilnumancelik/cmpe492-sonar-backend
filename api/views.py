import api
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import *
from rest_framework import viewsets
from api.serializers import *
from rest_framework import viewsets
from rest_framework import permissions

@api_view(['GET'])
def main_view(request):
    return Response('Hello World!')


@api_view(['GET'])
def article_lists(request):
    lists = ArticleList.objects.all()
    serializer = ArticleListResponseSerializer(
        lists,
        context = { 'is_successful': True,
                    'message': ""}
    )
    return Response(serializer.data)

@api_view(['GET'])
def article_list(request, list_id):
    article_list_id = list_id

    if article_list_id == None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    article_list = ArticleList.objects.filter(pk=article_list_id).first()
    if article_list is None:
        print('here')
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    dois_in_list = ArticleListToDOI.objects.filter(article_list=article_list).all()
    articles = []
    for doi in dois_in_list:
        article = Article.objects.filter(doi=doi.doi).first()
        print(article)
        if article is not None:
            articles.append(article) 

    serializer = ArticleListItemsResponseSerializer(
        articles,
        context = { 'is_successful': True, 'message': ""}
    )

    return Response(serializer.data)

@api_view(['GET'])
def get_graph(request, list_id):
    article_list_id = list_id

    if article_list_id == None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    article_list = ArticleList.objects.filter(pk=article_list_id).first()
    if article_list is None:
        print('here')
        return Response(status=status.HTTP_404_NOT_FOUND)

    nodes = Node.objects.filter(article_list=article_list).all()
    edges = Edge.objects.filter(article_list=article_list).all()

    serializer = GraphSerializer(
        {
            'nodes': nodes,
            'edges': edges
        }, context = { 'is_successful': True, 'message': ""}
    )

    return Response(serializer.data)
    



class DummyViewSet(viewsets.ModelViewSet):

    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Dummy.objects.all()
    serializer_class = DummySerializer