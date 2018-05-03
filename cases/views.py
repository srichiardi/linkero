from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.models import User

# Create your views here.
class Cases(LoginRequiredMixin, View):
    
    def get(self, request):
        return render(request, 'cases/cases.html')
