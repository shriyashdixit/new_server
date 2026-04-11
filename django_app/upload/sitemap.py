from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'monthly'

    pages = [
        ('homepage_main', 1.0),
        ('services_page', 0.8),
        ('skills_page', 0.8),
        ('work_page', 0.8),
        ('team_page', 0.7),
        ('culture_page', 0.6),
        ('careers_page', 0.7),
        ('blogs_page', 0.7),
        ('contact_page', 0.6),
    ]

    def items(self):
        return self.pages

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]
