from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
import locale
locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')


class Fallos(models.Model):
    nr = models.IntegerField(default=0)
    corte = models.CharField(max_length=100, blank=True, null=True)
    exp = models.CharField(max_length=100, blank=True, null=True)
    autos = models.CharField(max_length=150, blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    sobre = models.CharField(max_length=100, blank=True, null=True)
    text = models.TextField(max_length=999999, blank=True, null=True)
    actora = models.CharField(max_length=150, blank=True, null=True)
    demandada = models.CharField(max_length=150, blank=True, null=True)
    jueces = models.CharField(max_length=150, blank=True, null=True)

    voces = models.CharField(max_length=1000, blank=True, null=True)
    materia = models.CharField(max_length=9000, blank=True, null=True)

    slug = models.SlugField(unique=True, editable=False)

    def save(self, **kwargs):
        super(Fallos, self).save()
        # return reverse('details', (), {"slug": self.slug})
        # slug_str = "%s %s" % (self.autos, self.nr)
        self.slug = '%i-%s' % (self.pk, slugify(self.autos))
        # self.slug = slugify(slug_str) + str(self.pk)
        self.autos = self.autos.upper()
        self.actora = self.actora.upper()
        self.demandada = self.demandada.upper()
        self.corte = self.corte.upper()
        super(Fallos, self).save()

    def get_absolute_url(self):
        return reverse('details', args=[str(self.slug)])

    def __unicode__(self):
        return self.user
