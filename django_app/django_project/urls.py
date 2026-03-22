from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from upload import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Homepage only
    path('', views.homepage_main, name='homepage_main'),
]

# Serve static/media (only if needed)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)