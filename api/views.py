from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import Dummy
from rest_framework import viewsets
from api.serializers import DummySerializer
from rest_framework import viewsets
from rest_framework import permissions

@api_view(['GET'])
def main_view(request):
    return Response('Hello World!')


class DummyViewSet(viewsets.ModelViewSet):

    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Dummy.objects.all()
    serializer_class = DummySerializer