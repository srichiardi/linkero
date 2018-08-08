"""linkero URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth.views import login, logout, password_change, password_change_done

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^login/$', login, name='login', kwargs={'redirect_authenticated_user': True}),
    re_path(r'^logout/$', logout, name='logout'),
    re_path(r'^$', include('cases.urls')),
    #re_path(r'^password_change/$', password_change, name='password_change'),
    #re_path(r'^password_change/done/$', password_change_done, name='password_change_done'),
]
