# -*- coding: utf-8 -*-
from django.shortcuts import render
from textprocessor.models import Fallos
from .forms import formFallos
from django.conf import settings
from datetime import datetime
import os
import re
import locale
from collections import Counter
locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')


# Load SAIJ Tesauro.
with open('tesauro_dict.txt', 'r') as inf:
    d = eval(inf.read())


# Main information extraction and storing. TXT files are picked up from the
# media folder, parsed and key data is stored in the main database.
def cij(request):
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
                    deducido = get_deducido(text, actora, demandada)
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
                    deducido = ""
                    disidencia = ""
                    mayoria = ""
                    resultado = ""
                    origen = ""
                    anterior = ""

                # Create and store database objects for each TXT.
                Fallos.objects.get_or_create(nr=nr,
                                             corte=corte,
                                             tomo=tomo,
                                             autos=autos,
                                             fecha=fecha,
                                             tipo=tipo,
                                             text=text,
                                             actora=actora,
                                             demandada=demandada,
                                             deducido=deducido,
                                             mayoria=mayoria,
                                             disidencia=disidencia,
                                             resultado=resultado,
                                             origen=origen,
                                             anterior=anterior,
                                             legislacion=legislacion,
                                             materia=materia,
                                             voces=voces,
                                             )

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
    tomo_regex = re.compile('([\w|\d]\.\s?\d+\.\s?\w+)|(Competencia.*?\d+\.\s\w+)')
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


def get_tomos(text):
    tomo_regex = re.compile('([\w|\d]\.\s?\d+\.\s?\w+)|(Competencia.*?\d+\.\s\w+)')
    try:
        tomo = re.search(tomo_regex, text).group(0)
        tomo = re.sub('Competencia\s[N|n].', 'C.', tomo)
        tomo = re.sub('\s', '', tomo)
        return tomo
    except Exception:
        tomo = "NA"
    return tomo


def get_date(text):
    fecha_regex = re.compile('(\d+\sde\s\w+\sde\s[\d]+)')
    try:
        fecha = re.search(fecha_regex, text).group(0)
        fecha = datetime.strptime(fecha, '%d de %B de %Y')
        fecha = fecha.date()
        return fecha
    except Exception:
        pass


def get_tipo(text):
    try:
        tipo = str()
        try:
            tipo = re.search('\.\sProcuración General', text).group(0)
            if tipo is not None:
                tipo = "Dictamen de la Procuración"
        except Exception:
            tipo_regex = re.compile('([R|r]ecursos?(\s[D|d]e)?\s\w+)')
            tipo = re.search(tipo_regex, text).group(0)
            tipo = tipo.capitalize()
    except Exception:
        tipo = ""
    return tipo


def uncap_text(text):
    uncap_regex = re.compile('[A-Z]([A-Z]+)')
    mixcap_regex = re.compile('([a-z][A-ZÑÁÉÍÓÚ][A-ZÑÁÉÍÓÚ]?)')
    text = re.sub(uncap_regex, lambda m: m.group(0).capitalize(), text)
    text = re.sub(mixcap_regex, lambda m: m.group(0).lower(), text)
    return text


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
        demandada = re.sub('S\/|C\/', "", demandada)
        demandada = demandada.strip()
    except Exception:
        demandada = ""
    return demandada



def get_deducido(text, actora, demandada):
    try:
        inter_regex = re.compile('((deducido|interpuesto)\spor\s(el|la)?(.*?)en\sla)')
        deducido = re.search(inter_regex, text).group(4)
        ac = actora.split()[0]
        ac = re.sub(',', '', ac)
        de = demandada.split()[0]
        de = re.sub(',', '', de)
        if ac in deducido:
            deducido = "Actora"
        elif "actores" in deducido:
            deducido = "Actora"
        elif "actora" in deducido:
            deducido = "actora"
        elif de in deducido:
            deducido = "Demandada"
        elif "demandada" in deducido:
            deducido = "Demandada"
        deducido = deducido.strip()
        deducido = deducido.title()
    except Exception:
        deducido = ""
    return deducido


def get_disidencia(text):
    disidentes = ['Nolasco', 'Petracchi', 'Fayt', 'Maqueda', 'Argibay',
                  'Zaffaroni', 'Lorenzetti', 'Belluscio', 'Nazareno',
                  'Boggiano', "O'Connor", 'Levene', 'Lopez', 'Bossert',
                  'Vazquez']
    disidencia = []

    try:
        for j in disidentes:
            try:
                dis1 = re.findall('(\w+\s\(en\sdisidencia)', text)
                if len(dis1) > 0:
                    for d in dis1:
                        if j in d:
                            disidencia.append(j)
            except Exception:
                continue

        if (len(disidencia)) == 0:
            for j in disidentes:
                try:
                    dis2 = re.search('((juez|jueces|juezas|jueza).*?disidencias?)', text).group(0)
                    if j in dis2:
                        disidencia.append(j)
                except Exception:
                    continue

        disidencia = ", ".join(disidencia)
    except Exception:
        disidencia = ""
    return disidencia


def get_mayoria(text, disidencia):
    jueces = ['Nolasco', 'Petracchi', 'Fayt', 'Maqueda', 'Argibay', 'Zaffaroni',
              'Lorenzetti', 'Belluscio', 'Nazareno', 'Boggiano', "O'Connor",
              'Levene', 'Lopez', 'Bossert', 'Vazquez']
    mayoria = []
    for j in jueces:
        try:
            jue = re.search(j, text).group(0)
            mayoria.append(jue)
        except Exception:
            continue
    mayoria = ', '.join(mayoria)

    disidente = disidencia.split()
    for d in disidente:
        mayoria = re.sub(d, '', mayoria)
        mayoria = re.sub(',\s,', ',', mayoria).strip()

    return mayoria


def get_resultado(text):
    try:
        resultado = re.search('(Por\sello.*\.)|(Por\slos\sfundamentos.*\.)',
                              text).group(0).lower()
        rechaza = ['rechaza', 'desestima', 'inoficiosa', 'improcedente',
                   'caducidad', 'desestiman', 'inadmisible', 'inadmisibles',
                   'mal concedido', 'caduca', 'abstracta', 'nulidad',
                   'no presentado']
        admite = ['admitir', 'revoca', 'revocar', ' admisible', ' procedente',
                  ' procedentes', 'hace lugar', 'admiten']
        remite = ['remitirá', 'remitir', 'deberá entender', 'remitirse',
                  'competencia originaria', 'remítanse']

        all_keys = rechaza + admite + remite
        first_key = re.search("|".join(all_keys), resultado).group(0)

        if first_key in rechaza:
            resultado = 'Desestima'
        elif first_key in admite:
            resultado = 'Admite'
        elif first_key in remite:
            resultado = 'Remite'


    except Exception:
        resultado = ""
    return resultado


def get_origen(text):
    try:
        origen = re.search('origen:(\s.*?\.)', text).group(1)
        origen = origen.strip()
    except Exception:
        origen = ""
    return origen


def get_anterior(text):
    try:
        anterior = re.search('anteriores|anterioridad:(\s.*?\.)', text).group(1)
        anterior = anterior.strip()
    except Exception:
        anterior = ""
    return anterior


def get_legislacion(text):
    try:
        legislacion = []
        legis = re.findall(r'(ley\s\d+\.?\d+|decreto\s\d+\.?\d+)', text)
        for l in legis:
            if l not in legislacion:
                legislacion.append(l)
        legislacion = ", ".join(legislacion)
    except Exception:
        legislacion = ""
    return legislacion


def get_materia(tesauro, text):
    materia = []
    for k, v in tesauro.items():
        te = tesauro.get(k).get("te").split(',')
        tg = tesauro.get(k).get("tg").split(',')
        use = tesauro.get(k).get("use").split(',')
        up = tesauro.get(k).get("up").split(',')
        terms = te + tg + use + up
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
    return materia


def get_voces(tesauro, text):
    voces = []
    for k, v in tesauro.items():
        te = tesauro.get(k).get("te").split(',')
        tg = tesauro.get(k).get("tg").split(',')
        use = tesauro.get(k).get("use").split(',')
        up = tesauro.get(k).get("up").split(',')
        terms = te + tg + use + up
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
