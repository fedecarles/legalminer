from django.contrib import admin
from .models import Fallos
from .models import userProfile


# Register your models here.
class FallosAdmin(admin.ModelAdmin):
    list_display = ('nr', 'fecha', 'autos', 'jueces')

admin.site.register(Fallos, FallosAdmin)
admin.site.register(userProfile)
