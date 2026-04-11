from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from upload import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.homepage_main, name='homepage_main'),
    path('contact/', views.contact_page, name='contact_page'),
    path('services/', views.services_page, name='services_page'),
    path('skills/', views.skills_page, name='skills_page'),
    path('work/', views.work_page, name='work_page'),
    path('team/', views.team_page, name='team_page'),
    path('culture/', views.culture_page, name='culture_page'),
    path('careers/', views.careers_page, name='careers_page'),
    path('blogs/', views.blogs_page, name='blogs_page'),
]

# Serve static/media (only if needed)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)