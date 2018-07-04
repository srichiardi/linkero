
from django.urls import re_path
from cases.views import CasesView

urlpatterns = [
    # case management view
    re_path(r'^$', CasesView.as_view(), name='cases'),
]