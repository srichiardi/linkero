
from django.urls import re_path
from cases.views import Cases

urlpatterns = [
    # case management view
    re_path(r'^$', Cases.as_view(), name='cases'),
]