from django import forms
from django.conf import settings
import os


root = "/home/federico/Documents/LegalScraper/Files_CIJ"

# input_path_pdf = os.path.join(settings.MEDIA_ROOT, "input/pdf")
# input_files_pdf = os.listdir(input_path_pdf)
# input_path_txt = os.path.join(settings.MEDIA_ROOT, "input/txt")
# input_files_txt = os.listdir(input_path_txt)
# output_path = os.path.join(settings.MEDIA_ROOT, "output")
# output_files = os.listdir(output_path)
# input_options_pdf = zip(input_files_pdf, input_files_pdf)
# input_options_txt = sorted(zip(input_files_txt, input_files_txt))
# output_options = sorted(zip(output_files, output_files))

input_files_txt = []
for path, subdirs, files in os.walk(root):
    for name in files:
        input_files_txt.append(name)

input_options_txt = sorted(zip(input_files_txt, input_files_txt))

class formFallos(forms.Form):

    input_list = forms.MultipleChoiceField(widget=forms.SelectMultiple,
                                           choices=input_options_txt)
    output_list = forms.MultipleChoiceField(widget=forms.SelectMultiple,
                                            # choices=output_options,
                                            required=False)
