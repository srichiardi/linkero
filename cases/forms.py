# -*- coding: utf-8 -*-
from django import forms


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
    platform = forms.CharField(
        widget = forms.HiddenInput(attrs={"id" : "platform_name",
                                          "value" : "ebay"})
    )
    
    report_type = forms.CharField(
        widget = forms.HiddenInput(attrs={"id" : "report_type",
                                          "value" : "listings"})
    )
    query_title = forms.CharField()

    
class CaseRunForm(forms.Form):
    pass