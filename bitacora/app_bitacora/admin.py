from django.contrib import admin

from app_bitacora.models import Experimentos, Plantas, Registros

# Register your models here.
admin.site.register(Plantas)
admin.site.register(Experimentos)
admin.site.register(Registros)