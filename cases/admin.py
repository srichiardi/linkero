from django.contrib import admin

# Register your models here.
from cases.models import Platforms, Reports, Cases
  
admin.site.register(Platforms)
admin.site.register(Reports)
admin.site.register(Cases)