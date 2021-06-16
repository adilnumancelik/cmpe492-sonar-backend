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
import datetime
import xml.etree.ElementTree as ET
import json
from api.models import *
from api.queue_util import push_to_queue
from rest_framework.permissions import AllowAny

# To search doi url: PUBMED_DOI_SEARCH_BASE + DOI
# To get article data url: PUBMED_GET_BY_ID_BASE + ID
# To get full records url: PUBMED_GET_FULL_RECORD_BASE.format(ID)
PUBMED_DOI_SEARCH_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term="
PUBMED_GET_BY_ID_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id="
PUBMED_GET_FULL_RECORD_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&rettype=txt"
NUMBER_OF_TRIALS_ALLOWED = 3
#TODO These can be added to environmental variables
FETCHER_QUEUE_NAME = 'pubmed_fetcher_queue'
PROCESSOR_QUEUE_NAME = 'processor_queue'

# Pubmed Fethcer Endpoint
@api_view(['GET'])
@permission_classes([AllowAny])
def pubmed_fetcher_view(request, DOI):
    # This will be used to push to queue.
    doi_list = [DOI]
    # Get the article with given doi.
    article = Article.objects.filter(doi = DOI).first()
    if article is None:
        return Response("There is no article in the system with this doi.", status=status.HTTP_404_NOT_FOUND)

    can_try = article.try_count <= NUMBER_OF_TRIALS_ALLOWED
    
    # Increase the number of trials and save the article.
    article.try_count += 1
    article.save()

    if article.raw_data is None:
        article.status="failed"
        article.save()
    
    # Search DOI first
    try:
        doi_search_url = PUBMED_DOI_SEARCH_BASE + DOI
        search_raw = requests.get(doi_search_url).text
    except:
        if can_try:
            push_to_queue(FETCHER_QUEUE_NAME, doi_list)
        elif article.raw_data is not None:
            article.status = "to_be_processed"
            article.save()
            push_to_queue(PROCESSOR_QUEUE_NAME, doi_list)
        return Response("Could not search doi.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # Get article id from search result
    try:
        root = ET.fromstring(search_raw)
        article_id = root.findall("./IdList/Id")[0].text
        #article_id = root[3][0].text
    except:
        if can_try:
            push_to_queue(FETCHER_QUEUE_NAME, doi_list)
        elif article.raw_data is not None:
            article.status = "to_be_processed"
            article.save()
            push_to_queue(PROCESSOR_QUEUE_NAME, doi_list)
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
        elif article.raw_data is not None:
            article.status = "to_be_processed"
            article.save()
            push_to_queue(PROCESSOR_QUEUE_NAME, doi_list)
        return Response("Could not get article raw data.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    print(len(article_raw))
    # Insert raw data fields to article object and save
    article.pubmed_raw_data1 = article_raw
    article.pubmed_raw_data2 = fullrecord_raw
    article.fetched_date = datetime.datetime.now()
    article.status = "to_be_processed"
    article.save()

    # Push the fetched article's doi to Pubmed processor queue.
    push_to_queue(PROCESSOR_QUEUE_NAME, doi_list)
    return Response('Article is fetched from Pubmed.', status=status.HTTP_200_OK)





# Pubmed Processor Endpoint
@api_view(['GET'])
@permission_classes([AllowAny])
def pubmed_processor_view(request, DOI):
    article_obj = Article.objects.filter(doi = DOI).first()
    if article_obj is None:
        return Response("There is no article in the system with this doi.", status=status.HTTP_404_NOT_FOUND)

    article_obj.processed_date = datetime.datetime.now()
    article_obj.save()

    if article_obj.raw_data != None:
        #PROCESS ELSEVIER DATA

        data = json.loads(article_obj.raw_data)
        article = data['article']['abstracts-retrieval-response']
        authors = data['authors']
        topics = article['subject-areas']['subject-area']

        article_obj.title=article['coredata']['dc:title']
        article_obj.save()

        article_to_dois = ArticleListToDOI.objects.filter(doi = DOI)

        for article_to_doi in article_to_dois:
            article_list = article_to_doi.article_list
            existing_article_node = Node.objects.filter(article_list = article_list, object_key = DOI, node_type = 'article').first()
            '''
            If article node is not none it means that for this specific 
            article list given article is processed before, so no further processing required.
            '''
            if existing_article_node is None:

                article_list.processed_count += 1 
                if article_list.processed_count == article_list.number_of_articles:
                    article_list.status="done"
                article_list.save()

                article_node = Node(
                            node_type='article',
                            article_list=article_list,
                            object_key=DOI,
                            specific_information=json.dumps({})
                        )
                article_node.save()
                
                #PROCESS AUTHORS
                for author in authors:
                    author_data = author['author-retrieval-response'][0]
                    author_id = author_data['coredata']['dc:identifier'].split(':')[1]

                    author_node = Node.objects.filter(article_list=article_list).filter(node_type='author').filter(object_key=author_id).first()

                    if author_node is None:
                        author_node = Node(
                            node_type='author',
                            article_list=article_list,
                            object_key=author_id,
                            specific_information=json.dumps({})
                        )
                        author_node.save()
                    
                    author_article_edge = Edge(
                        edge_type="author_of",
                        from_node=author_node,
                        to_node=article_node,
                        specific_information=json.dumps({}),
                        article_list=article_list
                    )

                    author_article_edge.save()

                #PROCESS TOPICS
                for topic in topics:
                    topic_name = topic['$']
                    topic_node = Node.objects.filter(article_list=article_list).filter(object_key=topic_name).filter(node_type='topic').first()
                    if topic_node is None:
                        topic_node = Node(
                            node_type='topic',
                            article_list=article_list,
                            object_key=topic_name,
                            specific_information=json.dumps({})
                        )
                        topic_node.save()
                    
                    topic_article_edge = Edge(
                        edge_type="topic_of",
                        from_node=topic_node,
                        to_node=article_node,
                        specific_information=json.dumps({}),
                        article_list=article_list
                    )
                    topic_article_edge.save()

        return Response(status=status.HTTP_200_OK)




    raw_1 = article_obj.pubmed_raw_data1
    raw_2 = article_obj.pubmed_raw_data2
    
    root = ET.fromstring(raw_1)
    root2 = ET.fromstring(raw_2)

    # Get publication date. If this is not possible get completion date. If this is not possible assign default date.
    try:
        year = root2.findall("./PubmedArticle/MedlineCitation/Article/ArticleDate/Year")[0].text  
        month = root2.findall("./PubmedArticle/MedlineCitation/Article/ArticleDate/Month")[0].text  
        day = root2.findall("./PubmedArticle/MedlineCitation/Article/ArticleDate/Day")[0].text
        pubdate = datetime.datetime(int(year), int(month), int(day))
    except:
        try:
            year = root2.findall("./PubmedArticle/MedlineCitation/DateCompleted/Year")[0].text  
            month = root2.findall("./PubmedArticle/MedlineCitation/DateCompleted/Month")[0].text  
            day = root2.findall("./PubmedArticle/MedlineCitation/DateCompleted/Day")[0].text
            pubdate = datetime.datetime(int(year), int(month), int(day))
        except:
            pubdate = datetime.datetime(1900,1,1)
    
    
    # Get article title. If this is not possible assign default date. 
    try:
        title = root.findall("./DocSum/Item/[@Name='Title']")[0].text   
    except:
        title = "Article " + DOI


    # Get topics. If this is not possible topics can be empty. 
    try:
        topics_raw = root2.findall("./PubmedArticle/MedlineCitation/MeshHeadingList/MeshHeading/DescriptorName")
    except:
        topics_raw = []
    
    topic_list = []
    for t in topics_raw:
        topic_list.append(t.text)

    authors = root.findall("./DocSum/Item/[@Name='AuthorList']")[0]

    # Get authors.
    try:
        authors2 = root2.findall("./PubmedArticle/MedlineCitation/Article/AuthorList/Author")
    except:
        authors2 = []

    author_list = []
    for author2 in authors2:
        author_list.append(author2.findall("./ForeName")[0].text+ " "+author2.findall("./LastName")[0].text)

    '''
    Create article Nodes:
        # Find all article lists that contain the article with this doi
        # Find all nodes that belong to this article list and contain the article with this doi
        # Create the missing nodes for all article lists that contain the article with this doi
    '''
    article_to_dois = ArticleListToDOI.objects.filter(doi = DOI)

    for article_to_doi in article_to_dois:
        existing_article_node = Node.objects.filter(article_list = article_to_doi.article_list, object_key = DOI, node_type = 'article').first()
        if existing_article_node is None:
            article_list = article_to_doi.article_list
            article_list.processed_count += 1 
            if article_list.processed_count == article_list.number_of_articles:
                article_list.status="done"
            article_list.save()

            node_data = {
                'node_type': 'article',
                'article_list': article_to_doi.article_list.pk,
                'object_key': DOI,
                'specific_information': json.dumps({})
            }
            node_serializer = NodeSerializer(data = node_data)

            if node_serializer.is_valid():
                node_serializer.save()
            else:
                return Response(node_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    '''
    Create author Nodes:
        # Find all aritcle lists that contain the author
        # Find all nodes that belong to this article list and contain the author
        # Create the missing nodes for all article lists that contain the author
        # Perform this for all authors in author list
    '''
    for author in author_list:
        for article_to_doi in article_to_dois:
            existing_author_node = Node.objects.filter(article_list = article_to_doi.article_list, object_key = author, node_type = 'author').first()
            if existing_author_node is None:
                node_data = {
                    'node_type': 'author',
                    'article_list': article_to_doi.article_list.pk,
                    'object_key': author,
                    'specific_information': json.dumps({})
                }
                node_serializer = NodeSerializer(data = node_data)
                if node_serializer.is_valid():
                    node_serializer.save()
                else:
                    return Response(node_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    '''
    Create topic Nodes:
        # Find all aritcle lists that contain the author
        # Find all nodes that belong to this article list and contain the topic
        # Create the missing nodes for all article lists that contain the topic
        # Perform this for all topic in topic list
    '''
    for topic in topic_list:
        for article_to_doi in article_to_dois:
            existing_topic_node = Node.objects.filter(article_list = article_to_doi.article_list, object_key = topic, node_type = 'topic').first()
            if existing_topic_node is None:
                node_data = {
                    'node_type': 'topic',
                    'article_list': article_to_doi.article_list.pk,
                    'object_key': topic,
                    'specific_information': json.dumps({})
                }
                node_serializer = NodeSerializer(data = node_data)
                if node_serializer.is_valid():
                    node_serializer.save()
                else:
                    return Response(node_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    '''
    Create author_of edges:
        # Find all aritcle lists that contain the article with this doi
        # Find all edges that belong to this article list and between authors of this article and this article
        # Create the missing edges for all article lists that contain the article with this doi and authors of this article
    '''
    for article_to_doi in article_to_dois:
        for author in author_list:
            author_node = Node.objects.filter(article_list = article_to_doi.article_list, object_key = author, node_type = 'author').first()
            article_node = Node.objects.filter(article_list = article_to_doi.article_list, object_key = DOI, node_type = 'article').first()
            existing_edge = Edge.objects.filter(edge_type = "author_of", from_node = author_node, to_node = article_node).first()
            if existing_edge is None:
                edge_data = {
                        'edge_type': 'author_of',
                        'from_node': author_node.pk,
                        'to_node':article_node.pk,
                        'article_list':article_to_doi.article_list.pk,
                        'specific_information': json.dumps({ 'author_name': author, 'DOI': DOI })
                    }
                edge_serializer = EdgeSerializer(data = edge_data)
                if edge_serializer.is_valid():
                    edge_serializer.save()
                else:
                    return Response(edge_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    '''
    Create topic_of edges:
        # Find all article lists that contain the article with this doi
        # Find all edges that belong to this article list and between topics of this article and this article
        # Create the missing edges for all article lists that contain the article with this doi and topics of this article
    '''
    for article_to_doi in article_to_dois:
        article_node = Node.objects.filter(article_list = article_to_doi.article_list, object_key = DOI, node_type = 'article').first()
        for topic in topic_list:
            topic_node = Node.objects.filter(article_list = article_to_doi.article_list, object_key = topic, node_type = 'topic').first()
            existing_topic_of_edge = Edge.objects.filter(article_list = article_to_doi.article_list, from_node = article_node, to_node = topic_node, edge_type = 'topic_of').first()
            if existing_topic_of_edge is None:
                edge_data = {
                    'edge_type': 'topic_of',
                    'from_node': article_node.pk,
                    'to_node':topic_node.pk,
                    'article_list':article_to_doi.article_list.pk,
                    'specific_information': json.dumps({ 'DOI': DOI, 'topic_name': topic })
                }
                edge_serializer = EdgeSerializer(data = edge_data)
                if edge_serializer.is_valid():
                    edge_serializer.save()
                else:
                    return Response(edge_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    article_obj.title = title
    article_obj.processed_date = datetime.datetime.now()
    article_obj.save()

    return Response(DOI, status=status.HTTP_200_OK)
