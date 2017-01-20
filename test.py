#!/usr/bin/python3
import os
import sys
import re

proj_path = "/home/federico/Dropbox/legalminer/"
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "legalminer.settings")
sys.path.append(proj_path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from textprocessor.models import Fallos

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

with open('resultados.txt', 'r') as inf:
    d = eval(inf.read())


def cij_resultados(result, text):
    resultados = []
    section = re.sub('\s+', ' ', text)
    try:
        section = re.search(r'RESUELVE.*', section).group(0)
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


all_objects = Fallos.objects.all()


for o in all_objects:
    resultados = cij_resultados(d, o.text)
    print(resultados)
    o.resultados = resultados
    o.save()
