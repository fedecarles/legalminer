# -*- coding: utf-8 -*-
from django.shortcuts import (render, get_object_or_404, redirect, reverse,
                              HttpResponse, HttpResponseRedirect)
from django.contrib.auth.decorators import login_required
from textprocessor.models import Fallos
from textprocessor.models import User
from textprocessor.models import MyNotes
from textprocessor.models import MySearches
from textprocessor.models import MyLikes
from caseanalyzer.forms import MySearchForm
from .forms import userForm
from .forms import userProfileForm
from django.core.serializers.json import DjangoJSONEncoder
import json
import uuid
import pandas as pd


def inicio(request):
    form = MySearchForm(request.POST or None)
    return render(request, 'inicio.html', {'form': form})


def details(request, slug):
    liked = False
    instance = get_object_or_404(Fallos, slug=slug)
    usuario = request.user
    for l in instance.likes.all():
        if str(l) in str(usuario):
            liked = True
            print (liked)
    context = {
        'instance': instance,
        'liked': liked,
    }
    return render(request, 'details.html', context)


def like_button(request):
    if request.method == 'POST':
        user = request.user
        id = request.POST.get('pk', None)
        fallo = get_object_or_404(Fallos, pk=id)

        if fallo.likes.filter(id=user.id).exists():
            MyLikes.objects.filter(user=request.user, fallos=fallo).delete()
            fallo.likes.remove(user)
            liked = False
        else:
            MyLikes.objects.get_or_create(user=request.user, fallos=fallo)
            fallo.likes.add(user)
            liked = True

    context = {'likes_count': fallo.total_likes, 'liked': liked}
    return HttpResponse(json.dumps(context), content_type='application/json')


def dashboard(request, pk=None):
    if request.method == 'POST':
        pks = request.POST.getlist('seleccion')
        q = request.POST.get('query')

        force_layout = forceLayoutData(pks)
        case_data = caseData(pks)

        context = {
            'query': q,
            'force_layout': json.dumps(force_layout),
            'case_data': json.dumps(case_data, cls=DjangoJSONEncoder),
        }

    return render(request, 'dashboard.html', context)


# Profile views.
@login_required
def update_profile(request):
    """Profile view for logged user."""
    user = request.user
    profile = user.profile
    if request.method == 'POST':
        user_form = userForm(request.POST, instance=user)
        profile_form = userProfileForm(request.POST, instance=profile)
        if all([user_form.is_valid(), profile_form.is_valid()]):
            user_form.save()
            profile_form.save()
            instance_url = reverse('view_profile')+str(user.id)
            return redirect(instance_url)
    else:
        user_form = userForm(instance=user)
        profile_form = userProfileForm(instance=profile)
    return render(request, 'update_profile.html',
                  {'user_form': user_form, 'profile_form': profile_form})


@login_required
def view_profile(request, id=None):
    """Profile View for a user other than the logged user (not editable)."""
    userdata = User.objects.get(pk=id)
    notes = MyNotes.objects.filter(user=request.user)
    liked = MyLikes.objects.filter(user=request.user)
    searches = MySearches.objects.filter(user=request.user)
    fav_list = [fav.fallos for fav in liked]
    notes_list = [note for note in notes]
    searches_list = [search for search in searches]

    context = {
        "uuid": str(id),
        "req_id": str(request.user.id),
        "username": userdata.username,
        "nombre": userdata.first_name,
        "apellido": userdata.last_name,
        "email": userdata.email,
        "favs": fav_list,
        "notes": notes_list,
        "searches": searches_list,
    }
    return render(request, 'view_profile.html', context)


# Create JSON nodes and links list for D3 force layout chart. Most of the
# code is from Austin Taylor
# http://www.austintaylor.io/d3/python/pandas/2016/02/01/create-d3-chart-python-force-directed/
def forceLayoutData(pks):
    autos = []
    citas = []

    for pk in pks:
        instance = get_object_or_404(Fallos, pk=pk)
        autos.append(instance.autos)
        citas.append(instance.citados)

    df = pd.DataFrame({"autos": autos, "citas": citas})
    dffilter = df["citas"] != ""
    df = df[dffilter]
    df = df[:500]
    links = pd.concat([pd.Series(row['autos'], row['citas'].split('; '))
                       for _i, row in df.iterrows()]).reset_index()
    links.columns = ["target", "source"]
    grouped_links = links.groupby(["target", "source"]).size().reset_index()

    unique_id = pd.Index(grouped_links['source']
                         .append(grouped_links['target'])
                         .reset_index(drop=True).unique())

    temp_links_list = list(grouped_links.apply(lambda row:
                                               {"source": row['source'],
                                                "target": row['target'],
                                                "value": row[0]},
                                               axis=1))

    links_list = []
    for link in temp_links_list:
        record = {"value": link['value'],
                  "source": unique_id.get_loc(link['source']),
                  "target": unique_id.get_loc(link['target'])
                  }
        links_list.append(record)

    nodes_list = []
    for name in unique_id:
        nodes_list.append({"name": name})
    json_prep = {"nodes": nodes_list, "links": links_list}
    return json_prep


# Get selection data and return a dict.
def caseData(pks):
    leyes = []
    jueces = []
    voces = []
    materia = []
    citados = []
    resultados = []

    # Get data from database.
    instances = [get_object_or_404(Fallos, pk=i) for i in pks]
    fecha = [i.fecha for i in instances]
    autos = [i.autos for i in instances]
    corte = [i.corte for i in instances]
    sobre = [i.sobre for i in instances]
    provincia = [i.provincia for i in instances]
    [leyes.append(i.leyes) for i in instances]
    [jueces.append(i.jueces) for i in instances]
    [voces.append(i.voces) for i in instances]
    [materia.append(i.materia) for i in instances]
    [citados.append(i.citados) for i in instances]
    [resultados.append(i.resultados) for i in instances]
    num = [i.nr for i in instances]

    # Build dictionary with case data.
    case_data = []

    for p in range(len(num)):
        sub = {
            'fecha': fecha[p],
            'autos': autos[p],
            'corte': corte[p],
            'sobre': sobre[p],
            'provincia': provincia[p],
            'leyes': leyes[p].split(', '),
            'jueces': jueces[p].split(', '),
            'voces': voces[p].split(', '),
            'materia': materia[p].split(', '),
            'citados': citados[p].split('; '),
            'resultados': resultados[p].split(', '),
            }
        case_data.append(sub)
    return case_data


def saveNotes(request):
    if request.method == 'POST':
        user = request.user
        autos = request.POST.get('autos', None)
        text = request.POST.get('text', None)
        note = MyNotes.objects.get_or_create(autos=autos, text=text, user=user,
                                             note_id=str(uuid.uuid4())[:10])
        note.save()

    context = {}
    return HttpResponse(json.dumps(context), content_type='application/json')


def saveSearch(request):
    if request.method == 'POST':
        user = request.user
        search = request.POST.get('query', None)
        q = MySearches.objects.get_or_create(search=search, user=user)
        q.save()

    context = {}
    return HttpResponse(json.dumps(context), content_type='application/json')


def myNotes(request, note_id):
    instance = get_object_or_404(MyNotes, note_id=note_id)
    context = {
        'instance': instance,
    }
    return render(request, 'details.html', context)


def deleteNote(request, note_id):
    user = request.user.id
    get_object_or_404(MyNotes, note_id=note_id).delete()
    reverse_url = reverse('view_profile', kwargs={'id': user})
    return HttpResponseRedirect(reverse_url)


def deleteSearch(request, id):
    user = request.user.id
    get_object_or_404(MySearches, pk=id).delete()
    reverse_url = reverse('view_profile', kwargs={'id': user})
    return HttpResponseRedirect(reverse_url)
