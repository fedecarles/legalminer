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
from django.contrib.auth import views as auth_views
from caseanalyzer.forms import MySearchForm
from django.conf.urls import url, include
from django.contrib import admin
from textprocessor.views import cij
from caseanalyzer.views import inicio, analyzer, details

urlpatterns = [
    # admin url
    url(r'^admin/', admin.site.urls),

    # registration and login / logout urls
    url(r'^accounts/login/$', auth_views.login, name='auth_login'),
    url(r'^accounts/logout/$', auth_views.logout, name='auth_logout'),
    url(r'^accounts/', include('registration.backends.default.urls')),

    # start page
    url(r'^$', inicio, name='inicio'),

    # file processor
    url(r'^cij/', cij, name='cij'),

    # main search url
    url(r'search/$',
        search_view_factory(view_class=FacetedSearchView,
                            form_class=MySearchForm), name='haystack_search'),

    # dashboard url
    url(r'analyzer/$', analyzer, name='analyzer'),

    # Case full text url
    url(r'details/(?P<slug>[\w-]+)/$', details, name='details'),
]
