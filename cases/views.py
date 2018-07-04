from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.models import User
from cases.forms import CaseFilterForm, EbayListingForm
from cases.models import Cases, Reports
from datetime import datetime, timedelta
from django.http import JsonResponse
from pyexpat import errors


# Loading the "cases" page and pull filtered cases.
class Cases(LoginRequiredMixin, View):
    
    def get(self, request):
        if request.is_ajax():
            form = CaseFilterForm(request.GET)
            if form.is_valid():
                # query the cases table for cases of the user created between dates of one platform
                if form.cleaned_data['from_date'] == "":
                    # set the date 2 weeks before
                    from_datetime = datetime.now()- timedelta(days=15)
                else:
                    from_datetime = datetime.strptime(form.cleaned_data['from_date'], '%d/%m/%Y')
                    
                if form.cleaned_data['to_date'] == "":
                    to_datetime = datetime.now()
                else:
                    to_datetime = datetime.strptime(form.cleaned_data['to_date'], '%d/%m/%Y')
                    
                # making sure from date is always greater than to_date
                if to_datetime < from_datetime:
                    to_datetime = from_datetime + timedelta(days=1)
                    
#                 case_list = Cases.objects.filter(user=request.user,
#                                                   platform=form.cleaned_data['platform'],
#                                                   creation_date__gte=from_datetime,
#                                                   creation_date__lte=to_datetime).order_by('-query_id')
                case_list = Cases.objects.all()
                                                  
                return JsonResponse({'status' : 'success',
                                     'case_list' : case_list
                                     }, safe=False)
            # if form is invalid
            else:
                return JsonResponse({'status' : 'fail'}, safe=False)
                
        # if request is not ajax
        else:
            params = {}
            params['case_filter_form'] = CaseFilterForm()
            params['ebay_listing_form'] = EbayListingForm()
            return render(request, 'cases/cases.html', params)
        
    def post(self, request):
        if request.is_ajax():
            form = EbayListingForm(request.POST)
            if form.is_valid():
                q_title = form.cleaned_data['keywords'] + form.cleaned_data['seller_ids']
                case = Cases(
                    user = request.user,
                    platform = form.cleaned_data['platform'],
                    report_type = Reports.objects.filter(report_name = form.cleaned_data['report_type']),
                    query_title = q_title,
                    status = 'r')
                case.save()
                return JsonResponse({'status' : 'success'})
            
            # if form is invalid
            else:
                return JsonResponse({'status' : 'fail'})
                