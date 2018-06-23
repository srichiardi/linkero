# -*- coding: utf-8 -*-
from django import forms
from cases.ebaySettings import globalSiteMap


class CaseFilterForm(forms.Form):
    
    platform = forms.ChoiceField(
        label = "Platform",
        choices = (('ebay', 'eBay'), ('mercadolibre', 'MercadoLibre'), ('alegro', 'Alegro')),
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
    EBAY_SITES_CHOICES = (
        ('us', 'US',
         'uk', 'UK',
         'ca', 'Canada',
         'fr', 'France')
    )
    
    platform = forms.CharField(
        widget = forms.HiddenInput(attrs={"id" : "platform_name",
                                          "value" : "ebay"})
    )
    
    report_type = forms.CharField(
        widget = forms.HiddenInput(attrs={"id" : "report_type",
                                          "value" : "listings"})
    )
    
    ebay_sites = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs = {"class" : "form-control",
                                                     "id" : "ebay-sites"}),
        choices=EBAY_SITES_CHOICES
    )
    
    seller_ids = forms.CharField(required=False,
                                 label="Seller ids",
                                 widget=forms.Textarea(attrs = {"class" : "form-control",
                                                                "id" : "ebay-seller-id"}))
    
    keywords = forms.CharField(required=False,
                               label="Keywords",
                               widget=forms.Textarea(attrs = {"class" : "form-control",
                                                              "id" : "ebay-item-keywords"}))
    
    desc_search = forms.ChoiceField(required=False,
                                    label="search in description",
                                    widget=forms.CheckboxInput(attrs = {"class" : "form-control",
                                                                        "id" : "desc-search"}))
    
    send_to_email = forms.EmailField(required=True,
                                     label="Delivery email",
                                     widget=forms.EmailInput(attrs = {"class" : "form-control",
                                                                      "id" : "delivery-email-addr"}))

    
class CaseRunForm(forms.Form):
    pass