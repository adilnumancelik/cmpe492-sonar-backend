# Create your models here.
from django.db import models
from django.db.models.query import ModelIterable

ARTICLE_LIST_STATUS = ["phase_1", "phase_2", "done"]
ARTICLE_LIST_STATUS_CHOICES = [(ARTICLE_LIST_STATUS[i], str(i)) for i in range(len(ARTICLE_LIST_STATUS))]

ARTICLE_STATUS = ["to_be_fetched", "to_be_processed", "done"]
ARTICLE_STATUS_CHOICES = [(ARTICLE_STATUS[i], str(i)) for i in range(len(ARTICLE_STATUS))]

NODE_TYPE = ["Article", "Author", "Affiliation", "Country", "Topic"]
NODE_TYPE_CHOICES = [(NODE_TYPE[i], str(i)) for i in range(len(NODE_TYPE))]

# TODO These edge types will change. For now do not constrain edge type to these.
EDGE_TYPE = ["Co-Authorship", "Co-Affiliation", "Author of"]
EDGE_TYPE_CHOICES = [(EDGE_TYPE[i], str(i)) for i in range(len(EDGE_TYPE))]

class Dummy(models.Model):
    name = models.CharField(max_length=100, blank=False, default='')
    value = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['name']


class User(models.Model):
    email = models.CharField(max_length=256, null=False, blank=False)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    register_date = models.DateField(null=False, auto_now_add=True)


class ArticleList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length = 100, blank=False, default='Article List')
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=ARTICLE_LIST_STATUS_CHOICES,
                              default="phase_1", max_length=20)
    processed_count = models.IntegerField(default = 0)
    number_of_articles = models.IntegerField(default = 0)
    
    class Meta:
        ordering = ['created_date']


class ArticleListToDOI(models.Model):
    article_list = models.ForeignKey(ArticleList, on_delete=models.CASCADE, null=True)
    doi = models.CharField(max_length = 100)


class Article(models.Model):
    status = models.CharField(choices=ARTICLE_STATUS_CHOICES,
                              default="to_be_fetched", max_length=20)
    title = models.CharField(max_length = 100, blank=False, default='')
    doi = models.CharField(max_length = 100)
    raw_data = models.CharField(max_length = 10000)
    created_date = models.DateTimeField(auto_now_add=True)
    fetched_date = models.DateTimeField(blank=True)
    processed_date = models.DateTimeField(blank=True)
    try_count = models.IntegerField(default = 0)
    other_stuff = models.CharField(max_length = 10000)

    class Meta:
        ordering = ['created_date']


class Node(models.Model):
    node_type = models.CharField(choices=NODE_TYPE_CHOICES,
                              default="Article", max_length=50)
    article_list = article_list = models.ForeignKey(ArticleList, on_delete=models.CASCADE, null=True)
    specific_information = models.CharField(max_length = 10000)


class Edge(models.Model):
    # For now do not constrain edge types.
    # edge_type = models.CharField(choices=EDGE_TYPE_CHOICES, default="Co-Authorship", max_length=50)
    edge_type = models.CharField(default="", max_length=100)
    from_node = models.ForeignKey(Node, related_name='out_edge', on_delete=models.CASCADE)
    to_node = models.ForeignKey(Node, related_name='in_edge', on_delete=models.CASCADE)
    article_list = models.ForeignKey(ArticleList, on_delete=models.CASCADE, null=True)
    specific_information = models.CharField(max_length = 10000)