
from django.urls import re_path
from cases.views import CasesView, PasswordChange

urlpatterns = [
    # case management view
    re_path(r'^$', CasesView.as_view(), name='cases'),
    re_path(r'^settings/$', PasswordChange.as_view(), name='settings'),
]