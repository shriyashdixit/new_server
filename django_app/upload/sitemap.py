from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost, CaseStudy


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


class BlogPostSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def location(self, post):
        return reverse('blog_detail_page', kwargs={'slug': post.slug})

    def lastmod(self, post):
        return post.updated_at


class CaseStudySitemap(Sitemap):
    protocol = 'https'
    changefreq = 'monthly'
    priority = 0.85

    def items(self):
        return CaseStudy.objects.filter(is_published=True, body__gt='')

    def location(self, study):
        return reverse('work_detail_page', kwargs={'slug': study.slug})
