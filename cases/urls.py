
from django.urls import re_path
from cases.views import CasesView, PasswordChange, FileDownload, CaseDetailsView, DeleteCaseDetails

urlpatterns = [
    # case management view
    re_path(r'^$', CasesView.as_view(), name='cases'),
    re_path(r'^settings/$', PasswordChange.as_view(), name='settings'),
    re_path(r'^download_results/$', FileDownload.as_view(), name='download_results'),
    re_path(r'^case_details/$', CaseDetailsView.as_view(), name='case_details'),
    re_path(r'^delete_case/$', DeleteCaseDetails.as_view(), name='delete_case'),
]