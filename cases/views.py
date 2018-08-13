import json
import csv
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, JsonResponse
from cases.forms import CaseFilterForm, EbayListingForm
from cases.models import Platforms, CaseDetails, InputArgs, EbayItem, EbaySellerDetails
from datetime import datetime, timedelta
from cases.tasks import send_ebay_listing_report
from mongoengine import connect
from pandas.io.json import json_normalize
from pandas import merge


# Loading the "cases" page and pull filtered cases.
class CasesView(LoginRequiredMixin, View):
    
    def get(self, request):
        if request.is_ajax():
            form = CaseFilterForm(request.GET)
            if form.is_valid():
                # connect to mongo
                mongo_client = connect('linkerodb', username='linkero-user', password='123linkero123')
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
                if pltfm == "all":
                    pltfm_name = [ plt.name for plt in Platforms.objects.all() ]
                else:
                    pltfm_name = [pltfm]
                
                paginate_by = 20
                                              
                cases_qset = CaseDetails.objects(lnkr_user_id = request.user.id,
                                                 platform__in = pltfm_name,
                                                 creation_date__gte=from_datetime,
                                                 creation_date__lte=to_datetime).order_by('-lnkr_query_id').all()
                
                paginator = Paginator(cases_qset, paginate_by)
                
                page_nr = int(form.cleaned_data['page'])
                try:
                    page = paginator.page(page_nr)
                except PageNotAnInteger:
                    # show first page if page is missing or is not a number
                    page = paginator.page(1)
                except EmptyPage:
                    # if page is out of range show last page
                    page = paginator.page(paginator.num_pages)
                
                
                #serialized_cases = list(cases_queryset)
                cases_table = render_to_string('cases/cases_table.html', {'cases_list' : page})
                                                  
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
            # connect to Mongo
            mongo_client = connect('linkerodb', username='linkero-user', password='123linkero123')
            
            form = EbayListingForm(request.POST)
            if form.is_valid():
                if form.cleaned_data['seller_id'].strip():
                    q_title = form.cleaned_data['seller_id'].strip()
                else:
                    q_title = form.cleaned_data['keywords'].strip()
                
                if q_title:
                    # create a record with input details
                    query_input = CaseDetails(lnkr_user_id = request.user.id,
                              platform = 'eBay',
                              report_type = 'listing details',
                              status = 'running',
                              title = q_title,
                              input_args = InputArgs(**{ 'seller_id' : form.cleaned_data['seller_id'].strip(),
                                            'keywords' : form.cleaned_data['keywords'].strip(),
                                            'ebay_sites' : form.cleaned_data['ebay_sites'],
                                            'search_desc' : form.cleaned_data['desc_search']
                                            })
                              )
    
                    query_input.save()
                    q_id = query_input.lnkr_query_id
                    
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


class FileDownload(LoginRequiredMixin, View):
    
    def get(self, request):
        #if request.is_ajax():
        # connect to Mongo
        mongo_client = connect('linkerodb', username='linkero-user', password='123linkero123')
        query_id = int(request.GET['query_id'])
        
        # pull the data from mongoDB
        e_items = EbayItem.objects(lnkr_query_id=query_id)
        items_df = json_normalize(json.loads(e_items.to_json()))
        
        e_sellers = EbaySellerDetails.objects(lnkr_query_id=query_id)
        sellers_df = json_normalize(json.loads(e_sellers.to_json()))
        
        df = merge(items_df, sellers_df, left_on='Seller.UserID', right_on='UserID')
        
        file_name = CaseDetails.objects(lnkr_query_id=query_id).get().file_name
        
        headers = []
        main_headers = ["Seller.UserID", "ItemID", "ListingStatus", "Location", "Quantity", "QuantitySold", "CurrentPrice.Value",
                "CurrentPrice.CurrencyID", "Title", "GlobalShipping", "ShipToLocations",
                "BusinessSellerDetails.AdditionalContactInformation", "BusinessSellerDetails.Address.Street1", 
                "BusinessSellerDetails.Address.Street2", "BusinessSellerDetails.Address.CityName", 
                "BusinessSellerDetails.Address.StateOrProvince", "BusinessSellerDetails.Address.CountryName", 
                "BusinessSellerDetails.Address.Phone", "BusinessSellerDetails.Address.PostalCode", 
                "BusinessSellerDetails.Address.CompanyName", "BusinessSellerDetails.Address.FirstName", 
                "BusinessSellerDetails.Address.LastName", "BusinessSellerDetails.Email", "BusinessSellerDetails.LegalInvoice", 
                "BusinessSellerDetails.TradeRegistrationNumber", "BusinessSellerDetails.VATDetails.VATID", 
                "BusinessSellerDetails.VATDetails.VATPercent", "BusinessSellerDetails.VATDetails.VATSite", "Seller.FeedbackScore", 
                "Seller.PositiveFeedbackPercent"]
        df_headers = df.columns
        for hdr in main_headers:
            if hdr in df_headers:
                headers.append(hdr)
        df = df[headers]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=linkero_file.csv'
        writer = csv.DictWriter(response, fieldnames=headers)
        writer.writeheader()
        writer.writerows(df.to_dict('records'))
        
        return response
                
                
class PasswordChange(LoginRequiredMixin, View):
    
    def post(self, request):
        if request.is_ajax():
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                return JsonResponse({'status' : 'success'})
            else:
                errors_list = render_to_string('cases/errors_table.html', {'form' : form })
                return JsonResponse({'status' : 'failed',
                                     'errors_list' : errors_list })

    
    def get(self, request):
        form = PasswordChangeForm(request.user)
        params = {'form' : form }
        return render(request, 'registration/password_change.html', params)
    