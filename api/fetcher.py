from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import Dummy
from rest_framework import viewsets
from api.serializers import DummySerializer
from rest_framework import viewsets
from rest_framework import permissions
import requests

# TODO Implement Fethcer Endpoint
@api_view(['GET'])
def fetcher_view(request):
    x = {'name': 'asomevalue', 'value': 'aaa'}
    requests.post("https://boun-sonar.herokuapp.com/dummies/", data = x)
    return Response('Ok')





