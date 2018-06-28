"""IQAS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from huawei.views import num,suggest,search
from django.views.static import serve
from IQAS.settings import STATIC_ROOT
import xadmin

urlpatterns = [
    url(r'', xadmin.site.urls),
    url(r'^admin/', admin.site.urls),
    url(r'^num/', num),
    url(r'^static/(?P<path>.*)$',  serve, {"document_root":STATIC_ROOT}),
    url(r'^suggest/(?P<key_words>.*)$',suggest),
    url(r'^search/(?P<key_words>.*)$', search)

]
#全局500页面配置
handler500 = 'huawei.views.page_error'
#全局404页面配置
# handler404 = 'huawei.views.page_not_found'
