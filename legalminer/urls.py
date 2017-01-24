# -*- coding: utf-8 -*-
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
from caseanalyzer.views import (inicio, details, dashboard, update_profile,
                                view_profile, like_button, saveNotes,
                                saveSearch, myNotes, deleteNote, deleteSearch)

urlpatterns = [
    # admin url
    url(r'^admin/', admin.site.urls),

    # registration and login / logout urls
    url(r'^accounts/login/$', auth_views.login, name='auth_login'),
    url(r'^accounts/logout/$', auth_views.logout, name='auth_logout'),
    url(r'^accounts/', include('registration.backends.default.urls')),

    # start page
    url(r'^$', inicio, name='inicio'),

    # main search url
    url(r'search/$',
        search_view_factory(view_class=FacetedSearchView,
                            form_class=MySearchForm), name='haystack_search'),

    # dashboard url
    url(r'dashboard/$', dashboard, name='dashboard'),

    # Case full text url
    url(r'details/(?P<slug>[\w-]+)/$', details, name='details'),

    # Profile urls
    url(r'^update_profile/$', update_profile, name='update_profile'),
    url(r'^view_profile/$', view_profile, name='view_profile'),
    url(r'^view_profile/(?P<id>\d+)/$', view_profile, name='view_profile'),

    # Favorites url
    url(r'^like/$', like_button, name='like_button'),

    # Save Notes
    url(r'saveNotes/$', saveNotes, name='savenotes'),

    # Save Search
    url(r'saveSearch/$', saveSearch, name='savesearch'),

    # Delete Search
    url(r'^deletesearch/(?P<id>\d+)/$', deleteSearch, name='deletesearch'),

    # View MyNotes
    url(r'^mynotes/(?P<note_id>\w+-.)/$', myNotes, name='mynotes'),

    # Delete Note
    url(r'^delete/(?P<note_id>\w+-.)/$', deleteNote, name='deletenote'),

]
