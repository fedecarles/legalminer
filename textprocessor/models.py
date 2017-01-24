# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
import locale
import uuid
locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')


class userProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    compania = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile, new = userProfile.objects.get_or_create(user=instance)


class Fallos(models.Model):
    nr = models.IntegerField(default=0)
    corte = models.CharField(max_length=255, blank=True, null=True)
    exp = models.CharField(max_length=100, blank=True, null=True)
    autos = models.TextField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    sobre = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(max_length=9999999, blank=True, null=True)
    actora = models.CharField(max_length=255, blank=True, null=True)
    demandada = models.CharField(max_length=255, blank=True, null=True)
    jueces = models.CharField(max_length=255, blank=True, null=True)
    leyes = models.CharField(max_length=255, blank=True, null=True)
    citados = models.TextField(blank=True, null=True)
    lugar = models.CharField(max_length=150, blank=True, null=True)
    provincia = models.CharField(max_length=150, blank=True, null=True)
    voces = models.TextField(blank=True, null=True)
    materia = models.TextField(blank=True, null=True)
    resultados = models.CharField(max_length=255, blank=True, null=True)

    slug = models.SlugField(unique=True, editable=False, max_length=255)

    updated = models.DateTimeField(auto_now=True)

    likes = models.ManyToManyField(User, related_name="likes")

    @property
    def total_likes(self):
        return self.likes.count()

    def save(self, **kwargs):
        super(Fallos, self).save()
        # return reverse('details', (), {"slug": self.slug})
        # slug_str = "%s %s" % (self.autos, self.nr)
        self.slug = '%i-%s' % (self.pk, slugify(self.autos[:255]))
        # self.slug = slugify(self.autos) + "-" + str(self.pk)
        super(Fallos, self).save()

    def get_absolute_url(self):
        return reverse('details', args=[str(self.slug)])

    def __unicode__(self):
        return self.user


class MyLikes(models.Model):
    fallos = models.ForeignKey(Fallos)
    user = models.ForeignKey(User)
    date_added = models.DateTimeField(auto_now_add=True)


class MyNotes(models.Model):
    user = models.ForeignKey(User)
    note_id = models.CharField(max_length=11, unique=True,
                               default=str(uuid.uuid4())[:10])
    autos = models.TextField(blank=True, null=True)
    text = models.TextField(max_length=9999999, blank=True, null=True)

    def __unicode__(self):
        return self.user


class MySearches(models.Model):
    user = models.ForeignKey(User)
    search = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user
