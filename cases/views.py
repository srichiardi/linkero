from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.models import User
from cases.forms import CaseFilterForm, EbayListingForm


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
            params['case_filter_form'] = CaseFilterForm()
            params['ebay_listing_form'] = EbayListingForm()
            return render(request, 'cases/cases.html', params)
        
    def post(self, request):
        if request.is_ajax():
            form = EbayListingForm(request.POST)
            if form.is_valid():
                pass