"""gcNetData URL Configuration

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

from gcnet.views import get_dynamic_data, get_derived_data, get_model_stations, some_streaming_csv_view

urlpatterns = [
    path('models/', get_model_stations),
    path('dynamic/<str:model>/<str:lod>/<str:parameter>/<str:start>/<str:end>/', get_dynamic_data),
    path('derived/<str:model>/<str:lod>/<str:parameter>/<str:calc>/<str:start>/<str:end>/', get_derived_data),
    path('stream/', some_streaming_csv_view)
]
