# -*- coding: utf-8 -*-
from django import forms
from cases.models import Platforms, Reports
from cases.ebaySettings import globalSiteMap


class CaseFilterForm(forms.Form):
    
    list_choices = [(0, 'All')]
    list_choices.extend( [ (plt.id, plt.name) for plt in Platforms.objects.all() ] )
    PLATFORM_CHOICES = tuple(list_choices)
    #PLATFORM_CHOICES = ( (0, 'All'), (1, 'eBay'), (2, 'MercadoLibre'), (3, 'Alegro'), (4, 'Facebook'))
    
    platform = forms.ChoiceField(
        label = "Platform",
        choices = PLATFORM_CHOICES,
        widget = forms.Select(attrs = {"class" : "form-control",
                                       "id" : "platform"}),
        required = False
    )
    
    from_date = forms.CharField(
        label = "From",
        widget = forms.TextInput(attrs = {"class" : "form-control date-picker",
                                        "id" : "start-date",
                                        "placeholder" : "dd/mm/yyyy"}),
        required = False
    )
    
    to_date = forms.CharField(
        label = "to",
        widget = forms.TextInput(attrs = {"class" : "form-control date-picker",
                                        "id" : "end-date",
                                        "placeholder" : "dd/mm/yyyy"}),
        required = False
    )
    
    page = forms.CharField(
        widget = forms.HiddenInput(attrs={"value" : 1,
                                          "id" : "page-number"})
    )
    
    
class EbayListingForm(forms.Form):
    
    EBAY_SITES_CHOICES = ((key, globalSiteMap[key]['name']) for key in globalSiteMap.keys())
    
    platform = forms.CharField(
        widget = forms.HiddenInput(attrs={"value" : 1})
    )
    
    report_type = forms.CharField(
        widget = forms.HiddenInput(attrs={"value" : 1})
    )
    
    ebay_sites = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        choices=EBAY_SITES_CHOICES
    )
    
    seller_id = forms.CharField(required=False,
                                 label="Seller id",
                                 widget=forms.TextInput(attrs = {"class" : "form-control"})
                                 )
    
    keywords = forms.CharField(required=False,
                               label="Keywords",
                               widget=forms.TextInput(attrs = {"class" : "form-control"})
                               )
    
    desc_search = forms.BooleanField(required=False,
                                     label="Search in description",
                                     widget=forms.CheckboxInput()
                                     )
    
    send_to_email = forms.EmailField(required=True,
                                     label="Delivery email",
                                     widget=forms.EmailInput(attrs = {"class" : "form-control"})
                                     )

    
class CaseRunForm(forms.Form):
    pass