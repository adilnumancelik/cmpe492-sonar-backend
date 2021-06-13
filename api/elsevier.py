from os import stat
from api.views import article_list
from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from api.models import Dummy
from rest_framework import viewsets
from api.serializers import *
from rest_framework import viewsets
from rest_framework import permissions
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
import json
from api.models import *
from api.queue_util import push_to_queue
from rest_framework.permissions import AllowAny


PUBMED_FETCHER_QUEUE = 'pubmed_fetcher_queue'

@api_view(['POST'])
@permission_classes([AllowAny])
def elsevier_fetcher_save(request):
    doi = request.data.get("doi")
    fetch_status = request.data.get("status")
    result = request.data.get("result")

    if doi is None or fetch_status is None or result is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    article = Article.objects.filter(doi=doi).first()

    if article is None:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if fetch_status == 200:
        article.raw_data = result
        article.fetched_date = datetime.now()
        article.save()
    
    push_to_queue(PUBMED_FETCHER_QUEUE, [doi])

    return Response(status=status.HTTP_200_OK)
