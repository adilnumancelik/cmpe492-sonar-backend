from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import Dummy
from rest_framework import viewsets
from api.serializers import ArticleSerializer, DummySerializer
from rest_framework import viewsets
from rest_framework import permissions
import requests
import datetime
import xml.etree.ElementTree as ET
from api.models import Article
from api.queue_util import push_to_queue

# To search doi url: PUBMED_DOI_SEARCH_BASE + DOI
# To get article data url: PUBMED_GET_BY_ID_BASE + ID
# To get full records url: PUBMED_GET_FULL_RECORD_BASE.format(ID)
PUBMED_DOI_SEARCH_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term="
PUBMED_GET_BY_ID_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id="
PUBMED_GET_FULL_RECORD_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&rettype=txt"
NUMBER_OF_TRIALS_ALLOWED = 3
#TODO These can be added to environmental variables
FETCHER_QUEUE_NAME = 'fetcher_queue'
PUBMED_PROCESSOR_QUEUE_NAME = 'pubmed_processor_queue'

# Pubmed Fethcer Endpoint
@api_view(['GET'])
def pubmed_fetcher_view(request, DOI):
    # This will be used to push to queue.
    doi_list = [DOI]
    # Get the article with given doi.
    article = Article.objects.filter(doi = DOI).first()
    can_try = article.try_count <= NUMBER_OF_TRIALS_ALLOWED
    
    # Increase the number of trials and save the article.
    article.try_count += 1
    article.save()
    
    # Search DOI first
    try:
        doi_search_url = PUBMED_DOI_SEARCH_BASE + DOI
        search_raw = requests.get(doi_search_url).text
    except:
        if can_try:
            push_to_queue(FETCHER_QUEUE_NAME, doi_list)
        return Response("Could not search doi.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # Get article id from search result
    try:
        root = ET.fromstring(search_raw)
        article_id = root[3][0].text
    except:
        if can_try:
            push_to_queue(FETCHER_QUEUE_NAME, doi_list)
        return Response("Could not find article from search result.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Get article raw data.
    try: 
        article_url = PUBMED_GET_BY_ID_BASE + article_id
        article_raw = requests.get(article_url).text
        fullrecord_url = PUBMED_GET_FULL_RECORD_BASE.format(article_id)
        fullrecord_raw = requests.get(fullrecord_url).text
    except:
        if can_try:
            push_to_queue(FETCHER_QUEUE_NAME, doi_list)
        return Response("Could not get article raw data.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    print(len(article_raw))
    # Insert raw data fields to article object and save
    article.pubmed_raw_data1 = article_raw
    article.pubmed_raw_data2 = fullrecord_raw
    article.fetched_date = datetime.datetime.now()
    article.status = "to_be_processed"
    article.save()

    # Push the fetched article's doi to Pubmed processor queue.
    push_to_queue(PUBMED_PROCESSOR_QUEUE_NAME, doi_list)
    return Response('Article is fetched from Pubmed.', status=status.HTTP_200_OK)

# Pubmed Processor Endpoint
@api_view(['GET'])
def pubmed_processor_view(request, DOI):
    # TODO: Implement the processor.
    x = 1
    return Response(DOI, status=status.HTTP_200_OK)
