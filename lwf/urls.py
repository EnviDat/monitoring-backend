"""Monitoring Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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

from django.urls import path

from lwf.views import get_db_data, get_derived_data, get_lwf_models, get_db_data_greater_than

urlpatterns = [
    path('models/', get_lwf_models),
    path('data/<str:model>/<str:lod>/<str:parameter>/<str:start>/<str:end>/', get_db_data),
    path('derived/<str:model>/<str:lod>/<str:parameter>/<str:calc>/<str:start>/<str:end>/', get_derived_data),
    path('greaterthan/<str:model>/<str:lod>/<str:parameter>/<str:start>/<str:end>/<str:gt>/', get_db_data_greater_than),
]
