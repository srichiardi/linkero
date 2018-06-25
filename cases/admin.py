from django.contrib import admin

# Register your models here.
from cases.models import Platforms, Reports
 
admin.site.register(Platforms)
admin.site.register(Reports)
