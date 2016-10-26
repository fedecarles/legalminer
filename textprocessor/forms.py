from django import forms
from django.conf import settings
import os


input_path_pdf = os.path.join(settings.MEDIA_ROOT, "input/CSJN/pdf")
input_files_pdf = os.listdir(input_path_pdf)
input_path_txt = os.path.join(settings.MEDIA_ROOT, "input/CSJN/txt")
input_files_txt = os.listdir(input_path_txt)
output_path = os.path.join(settings.MEDIA_ROOT, "output")
output_files = os.listdir(output_path)
input_options_pdf = zip(input_files_pdf, input_files_pdf)
input_options_txt = sorted(zip(input_files_txt, input_files_txt))
output_options = sorted(zip(output_files, output_files))


class formFallos(forms.Form):

    input_list = forms.MultipleChoiceField(widget=forms.SelectMultiple,
                                           choices=input_options_txt)
    output_list = forms.MultipleChoiceField(widget=forms.SelectMultiple,
                                            choices=output_options,
                                            required=False)


input_cij_pdf_path = os.path.join(settings.MEDIA_ROOT, "input/CIJ/pdf")
input_cij_pdf_files = os.listdir(input_cij_pdf_path)
input_cij_txt_path = os.path.join(settings.MEDIA_ROOT, "input/CIJ/txt")
input_cij_txt_files = os.listdir(input_cij_txt_path)
cij_output_path = os.path.join(settings.MEDIA_ROOT, "output/CIJ/txt")
cij_output_files = os.listdir(cij_output_path)
input_cij_options_pdf = zip(input_cij_pdf_files, input_cij_pdf_files)
input_cij_options_txt = sorted(zip(input_cij_txt_files, input_cij_txt_files))
output_cij_options = sorted(zip(cij_output_files, cij_output_files))

class formCIJ(forms.Form):

    cij_input_list = forms.MultipleChoiceField(widget=forms.SelectMultiple,
                                           choices=input_cij_options_txt)
    cij_output_list = forms.MultipleChoiceField(widget=forms.SelectMultiple,
                                            choices=output_cij_options,
                                            required=False)
