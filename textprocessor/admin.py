from django.contrib import admin
from .models import Fallos
from .models import userProfile
from .models import MyNotes
from .models import MySearches
from .models import MyLikes


# Register your models here.
class FallosAdmin(admin.ModelAdmin):
    list_display = ('nr', 'fecha', 'autos', 'jueces')


admin.site.register(Fallos, FallosAdmin)
admin.site.register(userProfile)


admin.site.register(MyLikes)


class MyNotesAdmin(admin.ModelAdmin):
    list_display = ('user', 'autos')

admin.site.register(MyNotes, MyNotesAdmin)


class MySearchesAdmin(admin.ModelAdmin):
    list_display = ('user', 'search')

admin.site.register(MySearches, MySearchesAdmin)
