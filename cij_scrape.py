#!/usr/bin/python3
import os
import io
import sys
import re
import time
from datetime import datetime
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.request import urlopen
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox

proj_path = "/home/fedecarles/legalminer/"
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

# Load the webdriver.
browser = webdriver.PhantomJS("/usr/local/bin/phantomjs")
# browser = webdriver.Firefox()

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
browser.get("http://www.cij.gov.ar/sentencias.html")

# Check for meta index, follow.
try:
    meta_robots = browser.find_element_by_xpath("//meta[@name='robots']").get_attribute("content")
    if "index, follow" in meta_robots:
        print ("Allowed to Index, Follow")
        pass
    else:
        print ("Not allowed to Index, Follow")
        sys.exit() 
except Exception:
    print ("No meta robots, pass")
    pass

# browser.find_element_by_id('fecha_fallo_hasta_aux').click()
# browser.find_element_by_xpath('/html/body/div/div/a[1]/span').click()
# browser.find_element_by_xpath('//tr[5]/td[5]/a').click()
# browser.find_element_by_xpath('//form/div[6]/input[1]').submit()

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
        jueces = re.sub(r'\s-', ', ', jueces)
    except Exception:
        pass
    return jueces


def cij_actora(text):
    try:
        patterns = re.search('(.*?)C\/|S\/|ACTOR:(.*?)S\/|DENUNCIANTE:(.*?)S\/|QUERELLANTE:(.*?)S\/', text).groups()
        actora = [p for p in patterns if p is not None]
        actora = "".join(actora).strip()
    except Exception:
        actora = ""
    return actora


def cij_demandada(text):
    try:
        patterns = re.search('C\/(.*?)S\/|IMPUTADO:(.*?)S\/|DEMANDADO:(.*?)S\/|DENUNCIADO:(.*?)S\/',
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


def cij_provincia(lugar):
    prov_dict = {
        "BUENOS AIRES": ["BLANCA", "ROCA", "PLATA", "SAN MARTÍN", "SAN MARTIN"],
        "CHUBUT": ["COMODORO"],
        "CÓRDOBA": ["CÓRDOBA", "CORDOBA"],
        "CORRIENTES": ["CORRIENTES"],
        "FORMOSA": ["FORMOSA"],
        "JUJUY": ["JUJUY"],
        "MENDOZA": ["MENDOZA"],
        "ENTRE RÍOS": ["PARANÁ", "PARANA"],
        "MISIONES": ["POSADAS"],
        "SANTA FE": ["SANTA FE", "ROSARIO"],
        "NEUQUÉN": ["NEUQUEN", "NEUQUÉN"],
        "CHACO": ["RESISTENCIA"],
        "SALTA": ["SALTA"],
        "LA PAMPA": ["SANTA ROSA"],
        "TIERRA DEL FUEGO": ["FUEGO"],
        "TUCUMÁN": ["TUCUMAN", "TUCUMÁN"],
        "CAPITAL FEDERAL": ["FEDERAL"],
        "SAN JUAN": ["SAN JUAN"],
        "SAN LUIS": ["SAN LUIS"],
        "SANTA CRUZ": ["GALLEGOS", "SANTA CRUZ"],
        "LA RIOJA": ["LA RIOJA"],
        "CATAMARCA": ["CATAMARCA"],
        "SANTIAGO DEL ESTERO": ["SANTIAGO"]
        }
    for k, v in prov_dict.items():
        for i in v:
            if i in lugar:
                return k


# http://stackoverflow.com/questions/26413216/pdfminer3k-has-no-method-named-create-pages-in-pdfpage
def pdf_url_to_txt(url):
    text = ""
    try:
        f = urlopen(url).read()
        fp = io.BytesIO(f)
        parser = PDFParser(fp)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize('')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # Process each page contained in the document.
        for page in doc.get_pages():
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox):
                    text += lt_obj.get_text()
    except Exception as e:
       pass
    return text


# Start Scraping
date1 = browser.find_element_by_xpath("//div[6]/ul/li[4]").text
date2 = browser.find_element_by_xpath("//div[25]/ul/li[4]").text

tri = []
exp = []
aut = []
fec = []
url = []
nro = []
txt = []

# while (date1 == date2):
for o in range(4):
    tribunal = browser.find_elements_by_xpath("//div/ul[@class='info']/li[1]")
    expediente = browser.find_elements_by_xpath("//div/ul[@class='info']/li[2]")
    autos = browser.find_elements_by_xpath("//div/ul[@class='info']/li[3]")
    fecha = browser.find_elements_by_xpath("//div/ul[@class='info']/li[4]")
    links = browser.find_elements_by_xpath("//a[@class='download']")

    [tri.append(i.text) for i in tribunal]
    [exp.append(i.text) for i in expediente]
    [aut.append(i.text) for i in autos]
    [fec.append(i.text) for i in fecha]
    [url.append(i.get_attribute('href')) for i in links]

    pagina = browser.find_element_by_class_name("more").text

    element = WebDriverWait(browser, 5).until(
      EC.presence_of_element_located((By.XPATH, "//*")))

    print (pagina)
    print ("========")
    for i in fecha:
        print (i.text)
    for i in autos:
        print (i.text)

    sig = browser.find_element_by_class_name("next")
    sig.click()
    print ("click pressed")

    date1 = browser.find_element_by_xpath("//div[6]/ul/li[4]").text
    date2 = browser.find_element_by_xpath("//div[25]/ul/li[4]").text

[nro.append(re.search('\d+', i).group(0)) for i in url]
[txt.append(pdf_url_to_txt(i)) for i in url]

print (len(tri), len(exp), len(exp), len(aut), len(fec), len(url), len(nro), len(txt))

for o in range(len(nro)):
    text = re.sub('“|”', '"', txt[o])
    corte = tri[o].replace('Tribunal: ', '')
    expediente = exp[o].replace('Expediente N°: ', '')
    autos = aut[o].replace('Carátula: ', '').upper()
    fecha = fec[o].replace('Fecha de sentencia: ', '')
    fecha = datetime.strptime(fecha, '%d/%m/%Y')
    sobre = cij_sobre(autos)
    actora = cij_actora(autos)
    demandada = cij_demandada(autos)
    jueces = cij_jueces(text)
    leyes = cij_leyes(text)
    citas = cij_citas(text)
    lugar = cij_lugar(text)
    provincia = cij_provincia(lugar)
    materia = get_materia(d, text)
    voces = get_voces(d, text)

    instance = Fallos(nr=nro[o], corte=corte, exp=expediente, autos=autos,
                      fecha=fecha, text=text, sobre=sobre, actora=actora,
                      demandada=demandada, jueces=jueces, leyes=leyes,
                      citados=citas, lugar=lugar, provincia=provincia,
                      voces=voces, materia=materia)
    try:
        instance.save()
        print ('Saved Fallo {} of {}'.format(o, len(nro)))
     
    except Exception as e:
        print ('=======')
        print ('Fallo not saved')
        print (autos)
        print (e)
        pass

with open('scrape_log.txt', 'a') as f:
    f.write('{} {}\n'.format(fec[0], len(nro)))
