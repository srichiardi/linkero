from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from cases.forms import CaseFilterForm, EbayListingForm
from cases.models import Cases, Reports, Platforms
from datetime import datetime, timedelta
from django.http import JsonResponse
from pyexpat import errors
from cases.tasks import send_ebay_listing_report


# Loading the "cases" page and pull filtered cases.
class CasesView(LoginRequiredMixin, View):
    
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
                
                pltfm = form.cleaned_data['platform']
                if pltfm == '0':
                    cases_queryset = Cases.objects.filter(user=request.user,
                                                  creation_date__gte=from_datetime,
                                                  creation_date__lte=to_datetime)\
                                                  .select_related('platform', 'report_type')\
                                                  .order_by('-query_id')\
                                                  .values('query_id','platform__name','creation_date','query_title','status',
                                                          'report_type__report_name')
                else:
                    cases_queryset = Cases.objects.filter(user=request.user,
                                                  platform=pltfm,
                                                  creation_date__gte=from_datetime,
                                                  creation_date__lte=to_datetime)\
                                                  .select_related('platform', 'report_type')\
                                                  .order_by('-query_id')\
                                                  .values('query_id','platform__name','creation_date','query_title','status',
                                                          'report_type__report_name')
                    
                
                
                #serialized_cases = list(cases_queryset)
                cases_table = render_to_string('cases/cases_table.html', {'cases_list' : cases_queryset})
                                                  
                return JsonResponse({'status' : 'success',
                                     'case_list' : cases_table
                                     })
            # if form is invalid
            else:
                return JsonResponse({'status' : 'fail'})
                
        # if request is not ajax
        else:
            listing_form = EbayListingForm()
            listing_form.fields['send_to_email'].initial = request.user.email
            params = {}
            params['case_filter_form'] = CaseFilterForm()
            params['ebay_listing_form'] = listing_form
            return render(request, 'cases/cases.html', params)
        
    def post(self, request):
        if request.is_ajax():
            form = EbayListingForm(request.POST)
            if form.is_valid():
                if form.cleaned_data['seller_id'].strip():
                    q_title = form.cleaned_data['seller_id'].strip()
                else:
                    q_title = form.cleaned_data['keywords'].strip()
                
                if q_title:
                    # create a record with input details 
                    case = Cases(
                        user = request.user,
                        platform = Platforms.objects.get(id=form.cleaned_data['platform']),
                        report_type = Reports.objects.get(report_id = form.cleaned_data['report_type']),
                        query_title = q_title,
                        status = 'running')
                    case.save()
                    q_id = case.query_id
                    
                    # schedule the task
                    send_ebay_listing_report.delay(form.cleaned_data['send_to_email'].strip(),
                                                   query_id = q_id,
                                                   user_id=request.user.id,
                                                   seller_id=form.cleaned_data['seller_id'].strip(),
                                                   keywords=form.cleaned_data['keywords'].strip(),
                                                   ebay_sites=form.cleaned_data['ebay_sites'],
                                                   search_desc=form.cleaned_data['desc_search'])
                    
                    # return a successful submission
                    return JsonResponse({'status' : 'success'})
                
                else:
                    # return an error requesting that either the seller id or keyword be provided
                    return JsonResponse({'status' : 'fail',
                                         'error' : 'please provide either a seller id or keywords (or both)'})
            
            # if form is invalid
            else:
                        
                return JsonResponse({'status' : 'fail',
                                     'errors' : dict(form.errors.items())})
                