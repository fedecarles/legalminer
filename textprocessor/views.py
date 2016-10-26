# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Fallos
from .forms import formFallos
from .forms import formCIJ
from caseanalyzer.forms import MySearchForm
from django.forms import modelformset_factory
from django.conf import settings
from datetime import datetime
import os
import re
import csv
import shutil
import locale
import itertools
from collections import Counter
locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')


# Load SAIJ Tesauro.
with open('tesauro_dict.txt', 'r') as inf:
    d = eval(inf.read())


# Main information extraction and storing. TXT files are picked up from the
# media folder, parsed and key data is stored in the main database.
def fileManager(request):
    form = formFallos()
    if request.method == 'POST':
        form = formFallos(request.POST or None)
        if form.is_valid():

            file_names = form.cleaned_data["input_list"]

            for f in file_names:
                input_path = os.path.join(settings.MEDIA_ROOT, 'input/txt')
                output_path = os.path.join(settings.MEDIA_ROOT, 'output')
                fn = os.path.join(input_path, f)

                # Run the data extracting functions.
                text = get_text(fn)
                nr = re.search('\d+', f).group(0)
                autos = get_autos(text)
                tomo = get_tomos(text)
                fecha = get_date(text)
                # text = uncap_text(text)
                tipo = get_tipo(text)
                actora = get_actora(autos)
                demandada = get_demandada(autos, actora)
                legislacion = get_legislacion(text)
                materia = get_materia(d, text)
                voces = get_voces(d, text)
                corte = "Corte Suprema de Justicia de la Nación"

                # If the TXT is a Dictamen and not a Sentence, store only some
                # specific data.
                if "Dictamen de la Procuración" not in tipo:
                    disidencia = get_disidencia(text)
                    mayoria = get_mayoria(text, disidencia)
                    resultado = get_resultado(text)
                    text = text.replace(' Ii ', ' II ')
                    text = text.replace(' Ii.', ' II.')
                    text = text.replace(' li ', ' II ')
                    text = text.replace(' Iii ', ' III ')
                    text = text.replace(' Iii.', ' III.')
                    text = text.replace(' lii ', ' III ')
                    text = text.replace(' iV ', ' IV ')
                    text = text.replace(' Vi ', ' VI ')
                    text = text.replace(' Viii ', ' VIII ')
                    origen = get_origen(text)
                    anterior = get_anterior(text)
                else:
                    disidencia = ""
                    mayoria = ""
                    resultado = ""
                    origen = ""
                    anterior = ""

                # Create and store database objects for each TXT.
                # Fallos.objects.get_or_create(nr=nr,
                #                              corte=corte,
                #                              tomo=tomo,
                #                              autos=autos,
                #                              fecha=fecha,
                #                              tipo=tipo,
                #                              text=text,
                #                              actora=actora,
                #                              demandada=demandada,
                #                              mayoria=mayoria,
                #                              disidencia=disidencia,
                #                              resultado=resultado,
                #                              origen=origen,
                #                              anterior=anterior,
                #                              legislacion=legislacion,
                #                              materia=materia,
                #                              voces=voces,
                #                              )

                # Once the data is stored, move the TXT to the processed folder.
                # with open(os.path.join(output_path, item), 'w') as fp:
                #     fp.write(text)
                # shutil.move(os.path.join(input_path, item),
                #             os.path.join(output_path, item))

        context = {
                'form': form,
            }
        return render(request, 'filemanager.html', context)
    context = {
       'form': form,
    }
    return render(request, 'filemanager.html', context)


def get_text(file_name):
    with open(file_name, 'r') as f:
        text = f.read()
        # text = text.replace('\n', '')
        text = text.replace('\xad\n', '')
        # text = text.replace('\x0c', '')
        # text = text.replace('\x1f', '')
        text = re.sub('\s+', ' ', text)
        text = re.sub('-\d-?', '', text)
        text = re.sub('-\s', '', text)
        text = text.replace('5.a.', 'SA')
        text = text.replace('1t', 'lt')
        text = text.replace('1n', 'ln')
        text = re.sub('[aeiou](1)[aeiou]?', 'l', text)
        text = re.sub('[bcdfghjklmnpqrstvwxzPC](1)', 'l', text)
        text = re.sub('(1)[bcdfghjklmnpqrstvwxzPC]', 'l', text)
        text = re.sub('([-/\\\\\(\)!"+,&\'.]{2,})', '', text)
        text = text.replace('6n', 'ón')
        text = text.replace('5l', 'sl')
        text = text.replace('5l', 'sl')
        return text


def get_autos(text):
    autos_regex = re.compile('(.*?)(\.?\s?Buenos Aires\,(?!\sProvincia)|Visto|Año del Bicentenario Buenos Aires|Procuración General|PROCURACION GENERAL|Corte Suprema de Justicia)')
    tomo_regex = re.compile(
        '([\w|\d]\.\s?\d+\.\s?\w+)|(Competencia.*?\d+\.\s\w+)')
    try:
        autos = re.search(autos_regex, text).group(1)
        autos = re.sub(tomo_regex, '', autos)
        autos = re.sub('RECURSOS? DE HECHO', '', autos)
        autos = autos.replace('Y OTROS.', '')
        autos = autos.replace('y otros.', '')
        autos = autos.replace('y otro.', '')
        autos = autos.replace('(y otros)', '')
        autos = re.sub('(;|:|<|>|_|•|!|\"|\')', '', autos)
        autos = re.sub('ORIGINARIO', '', autos)
        autos = re.sub('\scl\s', ' c/ ', autos)
        autos = re.sub('\scI\s', ' c/ ', autos)
        autos = re.sub('\ssl\s', ' s/ ', autos)
        autos = re.sub('\ssI\s', ' s/ ', autos)
        autos = re.sub('\sSI\s', ' s/ ', autos)
        autos = re.sub('\ssi\s', ' s/ ', autos)
        autos = re.sub('\sci\s', ' s/ ', autos)
        autos = re.sub('\sCI\s', ' c/ ', autos)
        autos = re.sub('\scI\s', ' c/ ', autos)
        autos = re.sub('\sel\s', ' c/ ', autos)
        autos = re.sub('^\s?\.', '', autos)
        autos = re.sub('Año del Bicentenario', '', autos)
        autos = autos.lstrip().rstrip()
        autos = autos.lstrip(r'\.').lstrip(',')
        autos = autos.upper()
        return autos
    except Exception:
        autos = "NA"
        return autos


def get_date(text):
    fecha_regex = re.compile('(\d+\sde\s\w+\sde\s[\d]+)')
    try:
        fecha = re.search(fecha_regex, text).group(0)
        fecha = datetime.strptime(fecha, '%d de %B de %Y')
        fecha = fecha.date()
        return fecha
    except Exception:
        pass


def get_actora(autos):
    try:
        actora = re.search('(.*?)S?C?\/', autos).group(1)
        actora = actora.strip()
        actora = actora
    except Exception:
        actora = ""
    return actora


def get_demandada(autos, actora):
    try:
        demandada = re.sub(actora, "", autos)
        if "C/" in demandada:
            demandada = re.sub('S\/.*', "", demandada)
        else:
            demandada = re.sub('C\/\.?', "", demandada)
        demandada = re.sub('C\/\.?|S\/', "", demandada)
        demandada = demandada.strip()
    except Exception:
        demandada = ""
    return demandada


def get_materia(tesauro, text):
    materia = []
    for k, v in tesauro.items():
        te = tesauro.get(k).get("te").split(',')
        # tg = tesauro.get(k).get("tg").split(',')
        # use = tesauro.get(k).get("use").split(',')
        # up = tesauro.get(k).get("up").split(',')
        terms = te  # + tg + use + up
        for t in terms:
            pattern = re.compile(r'\b%s\b' % t)
            try:
                term = re.search(pattern, text).group(0)
                if term:
                    m = tesauro.get(k).get("ma")
                    materia.append(m)
            except Exception:
                pass
    counts = Counter(materia)
    materia = list(set(sorted(materia, key=counts.get, reverse=True)))
    materia = ", ".join(materia)
    materia = re.sub(r'^\,\s', "", materia)
    materia = re.sub(r'\,\s\,', ", ", materia)
    return materia.upper()


def get_voces(tesauro, text):
    voces = []
    for k, v in tesauro.items():
        te = tesauro.get(k).get("te").split(',')
        # tg = tesauro.get(k).get("tg").split(',')
        # use = tesauro.get(k).get("use").split(',')
        # up = tesauro.get(k).get("up").split(',')
        terms = te  # + use + up + tg
        for t in terms:
            pattern = re.compile(r'\b%s\b' % t)
            try:
                term = re.search(pattern, text).group(0)
                if term:
                    voces.append(k)
            except Exception:
                pass
    counts = Counter(voces)
    voces = list(set(sorted(voces, key=counts.get, reverse=True)))
    voces = ", ".join(voces)
    voces = re.sub(r'^\,\s', "", voces)
    voces = re.sub(r'\,\s\,', ", ", voces)
    return voces


def cij_text(file_name):
    with open(file_name, 'r') as f:
        text = f.read()
        # text = text.replace('\n', ' ')
        text = re.sub('(Fecha de firma:.*?(#\d+){3})', '', text)
        text = re.sub('((#\d+){3})', '', text)
        text = re.sub('“|”', '"', text)
        text = re.sub(r'\"\w\"', lambda pat: pat.group(0).replace('"', ''), text)
        # text = re.sub('\s+', ' ', text)
        return text


def cij_date(text):
    try:
        fecha_regex = re.compile('Fecha de firma:\s(\d+\/\d+\/\d+)')
        fecha = re.search(fecha_regex, text).group(1)
        fecha = datetime.strptime(fecha, '%d/%m/%Y')
        fecha = fecha.date()
        return fecha
    except Exception:
        pass


def cij_jueces(text):
    jueces = []
    try:
        section = re.search(r'Firmado.*?por:.*', text).group(0)
        section = section.replace(',', '')
        section = section.replace('-', 'Firmado por: ').upper()
        may = section.split("FIRMADO")
        for m in may:
            if ("SECRETARIO" not in m and "SECRETARIA" not in m and
                "(ANTE MI)" not in m):
                m = re.sub(r'\,.*', '', m)
                m = re.sub(r'POR:\s', '', m)
                m = re.sub('JUEZ.*', '', m)
                m = re.sub('JUEZ.*', '', m)
                m = re.sub('PRESIDENTE.*', '', m)
                m = re.sub(r'DRA\.', '', m)
                m = re.sub(r'DRES\.', '', m)
                m = re.sub(r'DR\.', '', m)
                m = re.sub(r'^\,\s.', '', m)
                jueces.append(m.strip())
        jueces = ", ".join(jueces)
        jueces  = re.sub(r'^\,\s', '', jueces)
    except Exception:
        pass
    return jueces


def dbEdit(request):
    FallosFormset = modelformset_factory(Fallos, exclude=('origen',
                                                          'anterior',
                                                          'date_image',
                                                          'signature_image',
                                                          'nr',
                                                          'tomo',
                                                          'legislacion',
                                                          'voces',
                                                          'materia'),
                                         extra=0)
    formset = FallosFormset(request.POST or None)
    if request.method == 'POST':
        context = {'formset': formset}
        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.save()
    else:
        query = Fallos.objects.all()
        paginator = Paginator(query, 50)
        page = request.GET.get('page')
        try:
            objects = paginator.page(page)
        except PageNotAnInteger:
            objects = paginator.page(1)
        except EmptyPage:
            objects = paginator.page(paginator.num_pages)
        page_query = query.filter(id__in=[object.id for object in objects])
        formset = FallosFormset(queryset=page_query)
        context = {'objects': objects, 'formset': formset}
    return render_to_response('dbedit.html', context,
                              context_instance=RequestContext(request))


def cij_actora(text):
    try:
        patterns = re.search('(.*?)C\/|S\/|ACTOR:(.*?)S\/', text).groups()
        actora = [p for p in patterns if p is not None]
        actora = "".join(actora).strip()
    except Exception:
        actora = ""
    return actora


def cij_demandada(text):
    try:
        patterns = re.search('C\/(.*?)S\/|IMPUTADO:(.*?)S\/|DEMANDADO:(.*?)S\/',
                             text).groups()
        demandada = [p for p in patterns if p is not None]
        demandada = "".join(demandada).strip()
    except Exception:
        demandada = ""
    return demandada


def cij_sobre(text):
    try:
        sobre = re.search('S\/(.*)', text).group(1).strip()
    except Exception:
        sobre = ""
    return sobre


def cij(request):
    form = MySearchForm()
    cijform = formCIJ()
    if request.method == 'POST':
        form = formCIJ(request.POST or None)
        if form.is_valid():

            file_names = form.cleaned_data["cij_input_list"]

            for f in file_names:
                input_path = os.path.join(settings.MEDIA_ROOT, 'input/CIJ/txt')
                output_path = os.path.join(settings.MEDIA_ROOT, 'output/CIJ/txt')
                fn = os.path.join(input_path, f)

                nr = f.replace('.txt', '')

                with open('cij_14-10-2016-22-10-2016.csv', 'r') as fr:
                    reader = csv.reader(fr)
                    for row in reader:
                        if nr in row[5]:

                            # Run the data extracting functions.
                            text = cij_text(fn)
                            autos = row[2].upper()
                            exp = row[1]
                            fecha = row[3]
                            fecha = datetime.strptime(fecha, '%d/%m/%Y')
                            fecha = fecha.date()
                            corte = row[0]
                            sobre = cij_sobre(autos)
                            actora = cij_actora(autos)
                            demandada = cij_demandada(autos)
                            materia = get_materia(d, text)
                            voces = get_voces(d, text)
                            jueces = cij_jueces(text)

                            # Create and store database objects for each TXT.
                            Fallos.objects.get_or_create(nr=nr,
                                                         corte=corte,
                                                         exp=exp,
                                                         autos=autos,
                                                         fecha=fecha,
                                                         sobre=sobre,
                                                         text=text,
                                                         actora=actora,
                                                         demandada=demandada,
                                                         jueces=jueces,
                                                         materia=materia,
                                                         voces=voces,
                                                         )

                # Once the data is stored, move the TXT to the
                # processed folder.
                # with open(os.path.join(output_path, f), 'w') as fw:
                #     fw.write(text)
                # shutil.move(os.path.join(input_path, f),
                #             os.path.join(output_path, f))

        context = {
                'form': form,
                'cijform': cijform,
            }
        return render(request, 'cij.html', context)
    context = {
       'form': form,
       'cijform': cijform,
    }
    return render(request, 'cij.html', context)
