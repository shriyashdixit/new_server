"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from upload.views import chatbot, env, tutorials_webpage, homepage_main, e_commerce
from algo_trading.views import import_csv, success_page, prediction_model
from onedrive_clone.views import upload_file, file_list, download_file

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", homepage_main, name='homepage_main'),
    path("tutorials_webpage", tutorials_webpage, name='tutorials_webpage'),
    path("e_commerce", e_commerce, name='e_commerce'),
    # path("", RedirectView.as_view(url=reverse_lazy('admin:index'))),
    path('import_csv/', import_csv, name='import_csv'),
    path('success/', success_page, name='success_page'),
    path('accounts/login/', RedirectView.as_view(url=reverse_lazy('admin:index'))),
    path('prediction_model/', prediction_model, name='prediction_model'),
    path('chatbot', chatbot, name='chatbot'),
    path('env', env, name='env'),

    path('upload/', upload_file, name='upload_file'),
    path('files/', file_list, name='file_list'),
    path('download/<int:file_id>/', download_file, name='download_file'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
