from django.contrib import admin
from .models import Fallos


# Register your models here.
class FallosAdmin(admin.ModelAdmin):
    list_display = ('nr', 'autos', 'jueces')
admin.site.register(Fallos, FallosAdmin)





