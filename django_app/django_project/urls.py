from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.http import HttpResponse
from upload import views
from upload.sitemap import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

handler404 = 'upload.views.error_404'
handler500 = 'upload.views.error_500'

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

    path('health', lambda r: HttpResponse('ok'), name='health'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

# Serve static/media (only if needed)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
