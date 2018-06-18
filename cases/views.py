from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.models import User
from cases.forms import CaseFilterForm


# Loading the "cases" page and pull filtered cases.
class Cases(LoginRequiredMixin, View):
    
    def get(self, request):
        if request.is_ajax():
            form = CaseFilterForm(request.GET)
            if form.is_valid():
                # query the cases table for cases of the user created between dates of one platform
                pass
        else:
            params = {}
            case_filter_form = CaseFilterForm()
            params['case_filter_form'] = case_filter_form
            return render(request, 'cases/cases.html', params)
