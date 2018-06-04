# -*- coding: utf-8 -*-
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset
from crispy_forms.bootstrap import FormActions
from bootstrap3_datetime.widgets import DateTimePicker

class CaseFilterForm(forms.Form):
    
    multicolon_select = forms.MultipleChoiceField(
        choices = (('ebay', 'eBay'), ('ml', 'MercadoLibre'), ('al', 'Alegro')),
    )
    
    from_date = forms.DateField(
        widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False})
    )
    
    to_date = forms.DateField(
        widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False})
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