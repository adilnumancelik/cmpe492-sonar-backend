"""sonar_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from api.views import DummyViewSet
from api import elsevier, views
from api import pubmed
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Sonar API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@sonar.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
# router.register(r'dummies', DummyViewSet)

urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('hello/', views.main_view),
    path('article-lists/', views.article_lists),
    path('article-list/<int:list_id>/', views.article_list),
    path('article-list/<int:list_id>/delete/', views.delete_article_list),
    path('article-list/<int:list_id>/graph/', views.get_graph),
    path('article-list/<int:list_id>/delete-graph/', views.delete_graph),
    path('article-list/create/', views.create_article_list),
    path('pubmed-fetch/<path:DOI>/', pubmed.pubmed_fetcher_view),
    path('pubmed-process/<path:DOI>/', pubmed.pubmed_processor_view),
    path('elsevier-save/', elsevier.elsevier_fetcher_save)
]
