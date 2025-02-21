"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from django.urls import include
from myapp import views
app_name="myapp"
urlpatterns = [
    path('admin/', admin.site.urls),
    path("home/", views.home, name="home"),
    path("uploadpdf/",views.uploadpdf,name="uploadpdf"),
    path("downloadpdf/",views.downloadpdf,name="downloadpdf"),
    path("download_all",views.download_all,name="download_all"),
    path('product_master/<str:item_name>/', views.product_master, name='product_master'),

]
