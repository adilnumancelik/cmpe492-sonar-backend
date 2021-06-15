from api.queue_util import push_to_queue
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
from functools import wraps
import jwt
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from api.utils import *

ELSEVIER_FETCHER_QUEUE_NAME = 'elsevier_fetcher_queue'

def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token

def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            decoded = jwt.decode(token, verify=False)
            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse({'message': 'You don\'t have access to this resource'})
            response.status_code = 403
            return response
        return decorated
    return require_scope

@api_view(['GET'])
@permission_classes([AllowAny])
def main_view(request):
    token = get_token_auth_header(request)
    return Response('Hello World!')


@api_view(['GET'])
def article_lists(request):
    lists = ArticleList.objects.filter(userId = str(request.user))
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

    article_list = ArticleList.objects.filter(pk=article_list_id, userId = str(request.user)).first()
    if article_list is None:
        return Response('Article list is not found.', status=status.HTTP_404_NOT_FOUND)
    
    dois_in_list = ArticleListToDOI.objects.filter(article_list=article_list).all()
    articles = []
    for doi in dois_in_list:
        article = Article.objects.filter(doi=doi.doi).first()
        if article is not None:
            articles.append(article) 

    serializer = ArticleListItemsResponseSerializer(
        articles,
        context = { 'is_successful': True, 'message': ""}
    )

    return Response(serializer.data)

@api_view(['Post'])
def create_article_list(request):
    '''
    Could not make swagger work here. 
    This is the request model:
    {
    "title" : "Name of article list",
    "doi_list": [
        "(DOI 1)",
        "(DOI 2)"
        ...
        ]
    }
    '''
    doi_list = request.data.get('doi_list')
    number_of_articles = len(doi_list)
    userId = str(request.user)

    article_list_data = {
        'title': request.data.get('title'), 
        'number_of_articles': number_of_articles,
        'userId': userId
    }

    serializer = ArticleListSerializer(data=article_list_data)
    new_article_list = ArticleList()
    if serializer.is_valid():
        new_article_list = serializer.save()
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    article_list_id = new_article_list.id
    
    articleToDoisToCreate = []

    for doi in doi_list:
        doi_data = ArticleListToDOI()
        doi_data.article_list = new_article_list
        doi_data.doi = doi
        articleToDoisToCreate.append(doi_data)

    ArticleListToDOI.objects.bulk_create(articleToDoisToCreate)

    articlesToCreate = []
    for doi in doi_list:
        existingArticle = Article.objects.filter(doi = doi)
        if len(existingArticle) > 0:
            continue

        article_data = Article()
        article_data.doi = doi
    
        articlesToCreate.append(article_data)

    Article.objects.bulk_create(articlesToCreate)

    # Push the dois to fetcher queue
    try:
        push_to_queue(ELSEVIER_FETCHER_QUEUE_NAME, doi_list)
    except:
        return Response("Failed to push to queue. Delete the recently created article list and create a new one.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['Delete'])
def delete_article_list(request, list_id):
    if list_id == None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    article_list = ArticleList.objects.filter(pk = list_id, userId = str(request.user))
    if article_list is None:
        return Response('Article list is not found.', status=status.HTTP_404_NOT_FOUND)
    
    article_to_dois = ArticleListToDOI.objects.filter(pk = list_id)
    nodes = Node.objects.filter(article_list = list_id)
    edges = Edge.objects.filter(article_list = list_id)
    article_to_dois.delete()
    article_list.delete()
    nodes.delete()
    edges.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET'])
def get_graph(request, list_id):
    article_list_id = list_id

    if article_list_id == None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    article_list = ArticleList.objects.filter(pk=article_list_id).first()
    if article_list is None:
        return Response('Article list is not found.', status=status.HTTP_404_NOT_FOUND)

    nodes = Node.objects.filter(article_list=article_list).all()
    edges = Edge.objects.filter(article_list=article_list).all()

    serializer = GraphSerializer(
        {
            'nodes': nodes,
            'edges': edges
        }, context = { 'is_successful': True, 'message': ""}
    )
    #return JsonResponse(serializer.data, safe=False,json_dumps_params={'ensure_ascii':False})
    return Response(serializer.data)

@api_view(['Delete'])
def delete_graph(request, list_id):
    if list_id == None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    article_list = ArticleList.objects.filter(pk = list_id, userId = str(request.user))
    if article_list is None:
        return Response('Article list is not found.', status=status.HTTP_404_NOT_FOUND)

    nodes = Node.objects.filter(article_list = list_id)
    edges = Edge.objects.filter(article_list = list_id)
    nodes.delete()
    edges.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)    

class DummyViewSet(viewsets.ModelViewSet):

    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Dummy.objects.all()
    serializer_class = DummySerializer
