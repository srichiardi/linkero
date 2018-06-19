# -*- coding: utf-8 -*-
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset
from crispy_forms.bootstrap import FormActions


class CaseFilterForm(forms.Form):
    
    platform = forms.ChoiceField(
        label = "Platform: ",
        choices = (('eb', 'eBay'), ('ml', 'MercadoLibre'), ('al', 'Alegro')),
        widget = forms.Select(attrs = {"class" : "form-control",
                                       "id" : "platform"}),
        required = False
    )
    
    from_date = forms.CharField(
        label = "From: ",
        widget = forms.TextInput(attrs = {"class" : "form-control date-picker",
                                        "id" : "start-date",
                                        "placeholder" : "dd/mm/yyyy"}),
        required = False
    )
    
    to_date = forms.CharField(
        label = "to: ",
        widget = forms.TextInput(attrs = {"class" : "form-control date-picker",
                                        "id" : "end-date",
                                        "placeholder" : "dd/mm/yyyy"}),
        required = False
    )


class CaseFilterFormOld(forms.Form):
    
    select = forms.ChoiceField(
        label = "Platform: ",
        choices = (('eb', 'eBay'), ('ml', 'MercadoLibre'), ('al', 'Alegro')),
        required = False
    )
    
    from_date = forms.CharField(
        label = "From: ",
        widget=forms.TextInput(),
        required = False
    )
    
    to_date = forms.CharField(
        label = "to: ",
        widget=forms.TextInput(),
        required = False
    )
    
    helper = FormHelper()
    helper.field_template = 'bootstrap3/layout/inline_field.html'
    helper.form_class = 'form-inline'
    helper.form_method = 'get'
    helper.layout = Layout(
        Field('select', id="platform", css_class="form-control", wrapper_class="form-group"),
        Field('from_date', id="start-date", css_class="form-control date-picker", wrapper_class="form-group"),
        Field('to_date', id="end-date", css_class="form-control date-picker", wrapper_class="form-group"),
        FormActions(
            Submit('filter', 'Filter', css_class="btn btn-default")
        )
    )
    
    
class CaseRunForm(forms.Form):
    pass