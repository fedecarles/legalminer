from haystack import indexes
from .models import Fallos


class FallosIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    autos = indexes.CharField(model_attr='autos', boost=1.125)
    sobre = indexes.CharField(model_attr='sobre', null=True)
    texto = indexes.CharField(model_attr='text')
    fecha = indexes.DateField(model_attr='fecha', null=True)
    jueces = indexes.CharField(model_attr='jueces', null=True)
    corte = indexes.CharField(model_attr='corte', null=True)
    # materia = indexes.CharField(model_attr='materia', faceted=True, null=True)
    # voces = indexes.CharField(model_attr='voces', faceted=True, null=True)

    def get_model(self):
        return Fallos

    def get_updated_field(self):
        return "updated"

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
