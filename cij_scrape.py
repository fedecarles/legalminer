import os
import sys
import re
import csv
import math
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


proj_path = "/home/federico/Dropbox/legalminer/"
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "legalminer.settings")
sys.path.append(proj_path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from textprocessor.models import Fallos

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

browser = webdriver.PhantomJS(
    "/home/federico/PhantomJS/phantomjs-1.9.8-linux-x86_64/bin/phantomjs")

# Ir a la página inicial de CIJ y realizar la búsqueda de fallos por voz simple
# de inconstitucionalidad.
browser.get("http://www.cij.gov.ar/sentencias.html")

# browser.find_element_by_id('fecha_fallo_desde_aux').click()
# browser.find_element_by_xpath('/html/body/div/div/a[2]/span').click()
# browser.find_element_by_xpath('/html/body/div/div/a[2]/span').click()
# browser.find_element_by_xpath('//tr[3]/td[7]/a').click()
#
# browser.find_element_by_id('fecha_fallo_hasta_aux').click()
# browser.find_element_by_xpath('//tr[4]/td[7]/a').click()
#
# browser.find_element_by_xpath('//form/div[6]/input[1]').submit()


nr = browser.find_element_by_xpath('//div[5]/div[1]/span').text
loops = 1 # math.ceil(int(nr) / 20)

tri = []
exp = []
aut = []
fec = []
url = []

for l in range(0, loops):
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
    element = WebDriverWait(browser, 5).until(
      EC.presence_of_element_located((By.XPATH, "//*")))
    try:
        browser.find_element_by_class_name("next").click()
    except Exception:
        pass
    print (autos)
    print ("pag " + str(l) + " de " + str(loops))

nro = [re.search('\d+', i).group(0) for i in url]


for o in range(len(tri)):
    corte = tri[o].replace('Tribunal: ', '')
    exp = exp[o].replace('Expediente N°: ', '')
    autos = aut[o].replace('Carátula: ', '')
    fecha = fec[o].replace('Fecha de sentencia: ', '')
    fecha = datetime.strptime(fecha, '%d/%m/%Y')
    instance = Fallos(nr=nro[o], corte=corte, exp=exp, autos=autos,
                      fecha=fecha)
    instance.save()
