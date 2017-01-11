from django import forms
from textprocessor.models import User
from textprocessor.models import userProfile
from haystack.forms import FacetedSearchForm


class MySearchForm(FacetedSearchForm):

    fecha_from = forms.DateField(required=False, input_formats=['%d/%m/%Y'])
    fecha_to = forms.DateField(required=False, input_formats=['%d/%m/%Y'])

    jueces = forms.CharField(required=False)
    corte = forms.CharField(required=False)
    actora = forms.CharField(required=False)
    demandada = forms.CharField(required=False)
    sobre = forms.CharField(required=False)
    materia = forms.CharField(required=False)
    voces = forms.CharField(required=False)

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(MySearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        # Check to see if a start_date was chosen.
        if self.cleaned_data['fecha_from']:
            sqs = sqs.filter(fecha__gte=self.cleaned_data['fecha_from'])

        if self.cleaned_data['fecha_to']:
            sqs = sqs.filter(fecha__lte=self.cleaned_data['fecha_to'])

        if self.cleaned_data['jueces']:
            sqs = sqs.filter(jueces=self.cleaned_data['jueces'])

        if self.cleaned_data['corte']:
            sqs = sqs.filter(corte__exact=self.cleaned_data['corte'])

        if self.cleaned_data['actora']:
            sqs = sqs.filter(actora=self.cleaned_data['actora'])

        if self.cleaned_data['demandada']:
            sqs = sqs.filter(demandada__exact=self.cleaned_data['demandada'])

        if self.cleaned_data['sobre']:
            sqs = sqs.filter(sobre=self.cleaned_data['sobre'])

        if self.cleaned_data['materia']:
            sqs = sqs.filter(materia__exact=self.cleaned_data['materia'])

        if self.cleaned_data['voces']:
            sqs = sqs.filter(voces__exact=self.cleaned_data['voces'])

        return sqs


class userForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')


class userProfileForm(forms.ModelForm):

    class Meta:
        model = userProfile
        exclude = ('user',)


