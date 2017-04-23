from django import forms
from .models import User
from .models import userProfile
from haystack.forms import FacetedSearchForm


class MySearchForm(FacetedSearchForm):

    fecha_from = forms.DateField(required=False, input_formats=['%d/%m/%Y'],
                                 widget=forms.TextInput(attrs={
                                     'placeholder': '...',
                                     'class': 'col-md-9'}))

    fecha_to = forms.DateField(required=False, input_formats=['%d/%m/%Y'],
                               widget=forms.TextInput(attrs={
                                   'placeholder': '...',
                                   'class': 'col-md-9'}))
    jueces = forms.CharField(required=False,
                             widget=forms.TextInput(attrs={'placeholder': '...',
                                                           'class': 'col-md-9'})
                             )
    corte = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'placeholder': '...',
                                                          'class': 'col-md-9'}))
    actora = forms.CharField(required=False,
                             widget=forms.TextInput(attrs={'placeholder': '...',
                                                           'class': 'col-md-9'})
                             )
    demandada = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={
                                    'placeholder': '...',
                                    'class': 'col-md-9'}))

    sobre = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'placeholder': '...',
                                                          'class': 'col-md-9'}))

    # materia = forms.CharField(required=False,
    #                           widget=forms.TextInput(attrs={
    #                               'placeholder': '...',
    #                               'class': 'col-md-9'}))

    # voces = forms.CharField(required=False,
    #                         widget=forms.TextInput(attrs={'placeholder': '...',
    #                                                       'class': 'col-md-9'}))

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

        # if self.cleaned_data['materia']:
        #     sqs = sqs.filter(materia__exact=self.cleaned_data['materia'])

        # if self.cleaned_data['voces']:
        #     sqs = sqs.filter(voces__exact=self.cleaned_data['voces'])

        return sqs


class userForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')


class userProfileForm(forms.ModelForm):

    class Meta:
        model = userProfile
        fields = ('compania',)
