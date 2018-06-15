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
        widget=forms.TextInput(attrs={"class":"form-control date-picker",
                                      "id" : "start-date"})
    )
    
    to_date = forms.CharField(
        widget=forms.TextInput(attrs={"class" : "form-control date-picker",
                                        "id" : "end-date"})
    )
    
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        'multicolon_select',
        'from_date',
        'to_date',
        FormActions(
            Submit('save_changes', 'Save changes', css_class="btn-primary"),
            Submit('cancel', 'Cancel'),
        )
    )
    
    
class CaseRunForm(forms.Form):
    pass