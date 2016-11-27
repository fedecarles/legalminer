# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Fallos
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
from collections import Counter
locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')


# Load SAIJ Tesauro.
with open('tesauro_dict.txt', 'r') as inf:
    d = eval(inf.read())


# Main information extraction and storing. TXT files are picked up from the
# media folder, parsed and key data is stored in the main database.

def cij(request):
    form = MySearchForm()
    cijform = formCIJ()
    if request.method == 'POST':
        form = formCIJ(request.POST or None)
        if form.is_valid():

            file_names = form.cleaned_data["cij_input_list"]
            input_path = os.path.join(settings.MEDIA_ROOT,
                                      'input/CIJ/txt')
            output_path = os.path.join(settings.MEDIA_ROOT,
                                       'output/CIJ/txt')

            with open(os.path.join(settings.MEDIA_ROOT,
                                   'cij_16102016.csv'),
                      'r') as fr:
                reader = csv.reader(fr)

                for row in reader:
                    for f in file_names:
                        fn = os.path.join(input_path, f)
                        nr = f.replace('.txt', '')

                        if row[5] in f:
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
                            citados = cij_citas(text)
                            leyes = cij_leyes(text)
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
                                                         leyes=leyes,
                                                         citados=citados,
                                                         jueces=jueces,
                                                         materia=materia,
                                                         voces=voces,
                                                         )

                            # Once the data is stored, move the TXT to the
                            # processed folder.
                            with open(os.path.join(output_path, f), 'w') as fw:
                                fw.write(text)
                            shutil.move(os.path.join(input_path, f),
                                        os.path.join(output_path, f))

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
        text = re.sub(r'\"\w\"', lambda pat: pat.group(0).replace('"', ''),
                      text)
        # text = re.sub('\s+', ' ', text)
        return text


def cij_date(text):
    try:
        fecha_regex = re.compile('Fecha de firma:\s(\d+\/\d+\/\d+)')
        fecha = re.search(fecha_regex, text).group(1)
        fecha = datetime.strptime(fecha, '%d/%m/%Y').date()
        return fecha
    except Exception:
        pass


def cij_jueces(text):
    jueces = []
    try:
        juez = re.findall(r'Firmado.*?por:.*', text)
        for j in juez:
            j = j.upper()
            if ("SECRETARIO" not in j and "SECRETARIA" not in j and "(ANTE MI)" not in j):
                j = re.sub(r'.*?:', '', j)
                j = re.sub(r'\,.*', '', j)
                j = re.sub('JUEZ.*', '', j)
                j = re.sub('JUEZ.*', '', j)
                j = re.sub('PRESIDENTE.*', '', j)
                j = re.sub(r'DRA\.', '', j)
                j = re.sub(r'DRES\.', '', j)
                j = re.sub(r'DR\.', '', j)
                j = re.sub(r'^\,\s.', '', j)
                j = j.strip()
                if j not in jueces:
                    jueces.append(j)
        jueces = ", ".join(jueces)
        jueces = re.sub(r'^\,\s', '', jueces)
    except Exception:
        pass
    return jueces


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


def cij_leyes(text):
    leyes = []
    text = text.replace('\s+', ' ').lower()
    try:
        ley = re.findall('ley\s\d+\.?\d+', text)
        for l in ley:
            if l not in leyes:
                leyes.append(l)
        leyes = ", ".join(leyes).upper()
    except Exception:
        leyes = ""
    return leyes


def cij_citas(text):
    citas = []
    text = re.sub('\s+', ' ', text)
    try:
        cita = re.findall('\"([^\"]*)\"', text)
        for c in cita:
            if "s/" in c or "c/" in c:
                if len(c) < 100:
                    if c not in citas:
                        citas.append(c)
        citas = "; ".join(citas).upper()
    except Exception:
        pass
    return citas


def cij_sobre(text):
    try:
        sobre = re.search('S\/(.*)', text).group(1).strip()
    except Exception:
        sobre = ""
    return sobre


def cij_lugar(autos):
    lugares = ["BAHÍA BLANCA", "BAHIA BLANCA", "COMODORO RIVADAVIA",
               "CORDOBA", "CÓRDOBA", "CORRIENTES", "FORMOSA", "GENERAL ROCA",
               "JUJUY", "LA PLATA", "MAR DEL PLATA", "MENDOZA", "PARANA",
               "PARANÁ", "POSADAS", "SANTA FE", "MISIONES", "NEUQUEN",
               "RESISTENCIA", "ROSARIO", "SALTA", "SAN MARTÍN", "SAN MARTIN",
               "SANTA ROSA", "TIERRA DEL FUEGO", "TUCUMAN", "TUCUMÁN",
               "CAPITAL FEDERAL"]
    lugar = next((l for l in lugares if l in autos), "CAPITAL FEDERAL")
    return lugar
