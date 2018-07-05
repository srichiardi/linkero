# -*- coding: utf-8 -*-
from django import forms
from cases.models import Platforms, Reports
from cases.ebaySettings import globalSiteMap


class CaseFilterForm(forms.Form):
    
    PLATFORM_CHOICES = ( (plt.id, plt.name) for plt in Platforms.objects.all() )
    
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
    
    
class EbayListingForm(forms.Form):
    
    EBAY_SITES_CHOICES = ((key, globalSiteMap[key]['name']) for key in globalSiteMap.keys())
    
    platform = forms.CharField(
        widget = forms.HiddenInput(attrs={"id" : "platform_name",
                                          "value" : 1})
    )
    
    report_type = forms.CharField(
        widget = forms.HiddenInput(attrs={"id" : "report_type",
                                          "value" : 1})
    )
    
    ebay_sites = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        choices=EBAY_SITES_CHOICES
    )
    
    seller_ids = forms.CharField(required=False,
                                 label="Seller ids",
                                 widget=forms.Textarea(attrs = {"class" : "form-control",
                                                                "id" : "ebay-seller-id",
                                                                "rows" : 5}))
    
    keywords = forms.CharField(required=False,
                               label="Keywords",
                               widget=forms.Textarea(attrs = {"class" : "form-control",
                                                              "id" : "ebay-item-keywords",
                                                              "rows" : 5}))
    
    desc_search = forms.BooleanField(required=False,
                                    label="Search in description",
                                    widget=forms.CheckboxInput(attrs = {"id" : "desc-search"})
                                     )
    
    send_to_email = forms.EmailField(required=True,
                                     label="Delivery email",
                                     widget=forms.EmailInput(attrs = {"class" : "form-control",
                                                                      "id" : "delivery-email-addr"}))

    
class CaseRunForm(forms.Form):
    pass