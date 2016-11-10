# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from textprocessor.models import Fallos
from caseanalyzer.forms import MySearchForm
from django.core.serializers.json import DjangoJSONEncoder
import json
import pandas as pd


def inicio(request):
    form = MySearchForm(request.POST or None)
    return render(request, 'inicio.html', {'form': form})


def details(request, slug):
    instance = get_object_or_404(Fallos, slug=slug)
    return render(request, 'details.html', {'instance': instance})


def analyzer(request, pk=None):
    form = MySearchForm(request.POST or None)
    if request.method == 'POST':

        # Get selected cases from checklist.
        pks = request.POST.getlist('seleccion')

        fechas = tableToDict(countDataTable(pks, 'fecha'))
        leyes = tableToDict(countDataTable(pks, 'leyes'))
        jueces = tableToDict(countDataTable(pks, 'jueces'))
        citados = tableToDict(countDataTable(pks, 'citados'))
        sobre = tableToDict(countDataTable(pks, 'sobre'))
        actora = tableToDict(countDataTable(pks, 'actora'))
        demandada = tableToDict(countDataTable(pks, 'demandada'))
        voces = tableToDict(countDataTable(pks, 'voces'))
        materia = tableToDict(countDataTable(pks, 'materia'))

        case_data = caseData(pks)

        context = {
            'form': form,
            'fechas': json.dumps(fechas, cls=DjangoJSONEncoder),
            'leyes': json.dumps(leyes),
            'jueces': json.dumps(jueces, cls=DjangoJSONEncoder),
            'citados': json.dumps(citados, cls=DjangoJSONEncoder),
            'sobre': json.dumps(sobre, cls=DjangoJSONEncoder),
            'actora': json.dumps(actora, cls=DjangoJSONEncoder),
            'demandada': json.dumps(demandada, cls=DjangoJSONEncoder),
            'voces': json.dumps(voces, cls=DjangoJSONEncoder),
            'materia': json.dumps(materia, cls=DjangoJSONEncoder),
            'case_data': json.dumps(case_data, cls=DjangoJSONEncoder),
        }

        return render(request, 'analyzer.html', context)


# Summarize data by count.
def countDataTable(pks, var):
    temp = []
    for pk in pks:
        selec = get_object_or_404(Fallos, pk=pk)
        temp.append(getattr(selec, var))
    if var == "citados":
        temp = "; ".join([str(i) for i in temp])
        temp = temp.split('; ')
    else:
        temp = ", ".join([str(i) for i in temp])
        temp = temp.split(', ')
    temp = list(filter(None, temp))
    result = pd.Series(temp).value_counts()
    result = pd.DataFrame(result).reset_index()
    result.columns = [var, 'cantidad']
    result['porcentaje'] = result['cantidad'] / result['cantidad'].sum() * 100
    result['porcentaje'] = result['porcentaje'].round(2)
    return result


# Pandas count DF to dictionary
def tableToDict(table):
    result = [dict([(colname, row[i]) for i,
                    colname in enumerate(table.columns)])
              for row in table.values]
    return result


# Get selection data and return a dict.
def caseData(pks):
    # Dict data placeholders.
    fecha = []
    leyes = []
    citados = []
    num = []

    # Get data from database.
    for pk in pks:
        instance = get_object_or_404(Fallos, pk=pk)
        fecha.append(instance.fecha)
        leyes.append(instance.leyes)
        citados.append(instance.citados)
        num.append(instance.nr)

    # Build dictionary with case data.
    case_data = {}

    for p in range(len(num)):
        sub = {
                'fecha': fecha[p],
                'leyes': leyes[p],
                'citados': citados[p],
                }
        case_data[num[p]] = sub
    return case_data
