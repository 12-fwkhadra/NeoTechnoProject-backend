"""
URL configuration for NeoTechnoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from NeoTechnoProject.auth import LoginAPI, AdminAPI, LogoutAPI
from NeoTechnoProject.database_init import data_init, update_Clients
from NeoTechnoProject.fetch_api import get_Clients, get_countries, export_Clients, get_trans_per_clients, get_currencies
from NeoTechnoProject.post_api import add_transaction

urlpatterns = [
    path('admin/', admin.site.urls),
    path('load-data/', data_init),
    path('update-db/', update_Clients),
    path('auth/login/', LoginAPI.as_view(), name='login_api'),
    path('auth/status/', AdminAPI.as_view(), name='admin_api'),
    path('auth/logout/', LogoutAPI.as_view(), name='logout_api'),
    path('clients/', get_Clients),
    path('clients/<int:cid>/', get_trans_per_clients),
    path('countries/', get_countries),
    path('currencies/', get_currencies),
    path('clients/export/', export_Clients),
    path('add_tran/', add_transaction),
]
