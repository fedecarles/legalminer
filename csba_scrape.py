#!/usr/bin/python3
import os
import sys
import re
import math
import time
from datetime import datetime
from collections import Counter
from selenium import webdriver

# proj_path = "/home/fedecarles/legalminer/"
proj_path = "/home/federico/Dropbox/legalminer/"
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "legalminer.settings")
sys.path.append(proj_path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from textprocessor.models import Fallos

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# Load SAIJ Tesauro.
with open('tesauro_dict.txt', 'r') as inf:
    d = eval(inf.read())

# Load results dict.
with open('resultados.txt', 'r') as inf:
    res = eval(inf.read())

# Load the webdriver.
browser = webdriver.PhantomJS("/usr/local/bin/phantomjs")
# browser = webdriver.Firefox()
# browser = webdriver.Chrome('/home/federico/chromedriver')

for retry in range(3):
    try:
        browser = webdriver.Firefox()
        break
    except:
        time.sleep(3)

# Check for robot.txt. As of Dec2016 there is no robot.txt
# try:
#     with urlopen("https://www.cij.gov.ar/robots.txt") as f:
#         print(f.read().decode("utf-8"))
# except Exception:
#     sys.exit()

# Ir a la página inicial de CIJ y realizar la búsqueda de fallos por voz simple
# de inconstitucionalidad.
browser.get("http://juba.scba.gov.ar/Busquedas.aspx")

# Check for meta index, follow.
try:
    meta_robots = browser.find_element_by_xpath(
        "//meta[@name='robots']").get_attribute("content")
    if "index, follow" in meta_robots:
        print("Allowed to Index, Follow")
        pass
    else:
        print("Not allowed to Index, Follow")
        sys.exit()
except Exception:
    print("No meta robots, pass")
    pass

desde = browser.find_element_by_id('txtExpresionBusquedaIntegral')
desde.clear()
desde.send_keys('FechaDesdeFallo:01/02/2016 Y FechaHastaFallo:28/02/2016')
browser.find_element_by_id('btnRealizarBusqueda').click()
time.sleep(10)

total = browser.find_element_by_id(
    'cphMainContent_RepeaterDatosResultados_lblCantidad_1').text
total = int(re.sub('.*de\s', '', total))
total = math.ceil(total / 20)

links = []

for p in range(1):
    urls = browser.find_elements_by_xpath('//td/div/div/table/tbody/tr/td/p/a')
    for u in urls:
        if u.get_attribute('href') not in links:
            links.append(u.get_attribute('href'))


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


def get_actora(text):
    try:
        patterns = re.search("""(.*?)C\/|(.*?)CONTRA|(.*?)S\/|
                             ACTOR:(.*?)S\/|DENUNCIANTE:(.*?)S\/|
                             QUERELLANTE:(.*?)S\/""", text).groups()
        actora = [p for p in patterns if p is not None]
        actora = "".join(actora).strip()
    except Exception:
        actora = ""
    return actora


def get_demandada(text):
    try:
        patterns = re.search("""C\/(.*?)\.\s|CONTRA(.*?)\.\s|
                             IMPUTADO:(.*?)S\/|DEMANDADO:(.*?)S\/|
                             DENUNCIADO:(.*?)S\/""", text).groups()
        demandada = [p for p in patterns if p is not None]
        demandada = "".join(demandada).strip()
    except Exception:
        demandada = ""
    return demandada


def get_sobre(text):
    try:
        sobre = re.sub(get_actora(text), '', text)
        sobre = re.sub(get_demandada(text), '', sobre)
        replacements = "CONTRA|C/|S/|\.|Y OTRO"
        sobre = re.sub(replacements, '', sobre)
    except Exception:
        sobre = ""
    return sobre.strip()


def get_leyes(text):
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


def get_citas(text):
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


def get_resultados(result, text):
    resultados = []
    section = re.sub('\s+', ' ', text)
    try:
        section = re.search(r'S E N T E N C I A.*', section).group(0)
    except Exception:
        section = ""
    for k, v in result.items():
        for i in v:
            pattern = re.compile(r'%s' % i)
            try:
                term = re.search(pattern, section.lower()).group(0)
                if term:
                    resultados.append(k)
            except Exception:
                pass
    resultados = ", ".join(resultados)
    return resultados


count = 0
for l in links:
    browser.get(l)
    browser.find_element_by_id('cphMainContent_lnkDatosFallo').click()
    time.sleep(1)
    text = browser.find_element_by_xpath(
        "//div[3]/table[2]/tbody/tr[3]/td").text
    corte = browser.find_element_by_id('lblTribunalEmisor').text
    expediente = browser.find_element_by_id('lblCausa').text
    autos = browser.find_element_by_id('lblCaratula').text.upper()
    fecha = browser.find_element_by_id('lblFecha').text
    fecha = datetime.strptime(fecha, '%d/%m/%Y')
    sobre = get_sobre(autos)
    actora = get_actora(autos)
    demandada = get_demandada(autos)
    jueces = browser.find_element_by_id('lblmagistradosVotantes').text
    jueces = re.sub('-', ', ', jueces).upper()
    leyes = get_leyes(text)
    citas = get_citas(text)
    provincia = "BUENOS AIRES"
    materia = get_materia(d, text)
    voces = get_voces(d, text)
    resultados = get_resultados(res, text)
    lugar = "LA PLATA"
    count += 1

    instance = Fallos(corte=corte, exp=expediente, autos=autos,
                      fecha=fecha, text=text, sobre=sobre, actora=actora,
                      demandada=demandada, jueces=jueces, leyes=leyes,
                      citados=citas, lugar=lugar, provincia=provincia,
                      voces=voces, materia=materia, resultados=resultados)
    try:
        instance.save()
        print('Saved Fallo {} of {}'.format(count, len(links)))

    except Exception as e:
        print('=======')
        print('Fallo not saved')
        print(autos)
        print(e)
        pass

with open('scrape_log.txt', 'a') as f:
    f.write('{} {}\n'.format(datetime.now(), len(links)))
