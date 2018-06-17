# -*- coding: utf-8 -*-
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset
from crispy_forms.bootstrap import FormActions

class CaseFilterForm(forms.Form):
    
    multicolon_select = forms.MultipleChoiceField(
        choices = (('ebay', 'eBay'), ('ml', 'MercadoLibre'), ('al', 'Alegro')),
    )
    
    from_date = forms.CharField(
        label = "From: ",
        widget=forms.TextInput()
    )
    
    to_date = forms.CharField(
        label = "to: ",
        widget=forms.TextInput(attrs={"class" : "form-control date-picker",
                                        "id" : "end-date"})
    )
    
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('multicolon_select', id="platform", css_class="form-control"),
        Field('from_date', id="start-date", css_class="form-control date-picker"),
        'to_date',
        FormActions(
            Submit('filter', 'Filter', css_class="btn btn-default")
        )
    )
    
    
class CaseRunForm(forms.Form):
    pass