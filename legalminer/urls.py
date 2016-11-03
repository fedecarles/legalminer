"""legalminer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from haystack.views import FacetedSearchView, search_view_factory
from caseanalyzer.forms import MySearchForm
from django.conf.urls import url
from django.contrib import admin
from textprocessor.views import cij, dbEdit
from caseanalyzer.views import analyzer, details

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^cij/', cij),
    url(r'^dbedit/', dbEdit),
    url(r'search/$',
        search_view_factory(view_class=FacetedSearchView,
                            form_class=MySearchForm), name='haystack_search'),
    url(r'analyzer/$', analyzer, name='analyzer'),
    url(r'details/(?P<slug>[\w-]+)/$', details, name='details'),
]
