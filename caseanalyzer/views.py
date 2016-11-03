# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from textprocessor.models import Fallos
from caseanalyzer.forms import MySearchForm
from django.core.serializers.json import DjangoJSONEncoder
import json
import pandas as pd


def details(request, slug):
    instance = get_object_or_404(Fallos, slug=slug)
    return render(request, 'details.html', {'instance': instance})


def analyzer(request, pk=None):
    form = MySearchForm(request.POST or None)
    if request.method == 'POST':

        # Get selected cases from checklist.
        pks = request.POST.getlist('seleccion')

        # Get case data and return a dict.
        case_data = caseData(pks)

        # Summarize votes by Justice and return a dict.
        summary_votes = summarizeVotes(case_data)
        summary_votes = [dict([(colname, row[i]) for i,
                               colname in enumerate(summary_votes.columns)])
                         for row in summary_votes.values]

        # Summarize case data by date and return a dict.
        case_dates = caseDates(case_data)
        case_dates = [dict([(colname, row[i]) for i,
                            colname in enumerate(case_dates.columns)])
                      for row in case_dates.values]

        context = {
            'form': form,
            'case_data': json.dumps(case_data, ensure_ascii=False,
                                    cls=DjangoJSONEncoder),
            'summary_votes': summary_votes,
            'case_dates': json.dumps(case_dates, cls=DjangoJSONEncoder),
        }

        return render(request, 'analyzer.html', context)


# Summarize data by justice.
def summarizeVotes(data):
    df = pd.DataFrame(data)
    df_mayoria1 = df.loc['jueces'].str.split('\s*,\s').apply(pd.Series)
    df_mayoria2 = df_mayoria1.stack().rename('value').reset_index()
    df_mayoria = pd.crosstab(df_mayoria2.level_0, df_mayoria2.value)

    sum_mayoria = df_mayoria.sum()
    por_mayoria = df_mayoria.sum() / len(df_mayoria) * 100
    por_mayoria = por_mayoria.round(2)

    df_list = [sum_mayoria, por_mayoria]
    result = pd.concat(df_list, axis=1)
    result = result[result.index != ""]
    result = result.fillna(0)
    result["jueces"] = result.index
    result.columns = ['q_may', 'p_may', 'jueces']
    return result


# Summarize data by dates.
def caseDates(data):
    df = pd.DataFrame(data)
    result = df.loc['fecha']
    result = result.groupby(result, sort=False).size()
    result = pd.DataFrame(result)
    result["fecha"] = result.index
    result.columns = ['count', 'fecha']
    return result


# Get selection data and return a dict.
def caseData(pks):
    # Dict data placeholders.
    autos = []
    texto = []
    fecha = []
    actora = []
    demandada = []
    jueces = []
    num = []

    # Get data from database.
    for pk in pks:
        instance = get_object_or_404(Fallos, pk=pk)
        autos.append(instance.autos)
        texto.append(instance.text)
        fecha.append(instance.fecha)
        actora.append(instance.actora)
        demandada.append(instance.demandada)
        jueces.append(instance.jueces)
        num.append(instance.nr)

    # Build dictionary with case data.
    case_data = {}

    for p in range(len(num)):
        sub = {
                'autos': autos[p],
                'texto': texto[p],
                'fecha': fecha[p],
                'actora': actora[p],
                'demandada': demandada[p],
                'jueces': jueces[p],
                }
        case_data[num[p]] = sub
    return case_data
