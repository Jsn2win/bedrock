import json

from django.conf import settings
from django.db import models, transaction

SITEMAPS_DATA = settings.SITEMAPS_PATH.joinpath('data')


def load_sitemaps_data():
    with SITEMAPS_DATA.joinpath('etags.json').open() as fh:
        etags = json.load(fh)

    with SITEMAPS_DATA.joinpath('sitemap.json').open() as fh:
        sitemap = json.load(fh)

    return sitemap, etags


def get_sitemap_objs():
    objs = []
    sitemap, etags = load_sitemaps_data()
    for url, locales in sitemap.items():
        if not locales:
            locales = [""]

        for locale in locales:
            if locale:
                full_url = f"{settings.CANONICAL_URL}/{locale}{url}"
            else:
                full_url = f"{settings.CANONICAL_URL}{url}"

            kwargs = {"path": url, "locale": locale}
            etag = etags.get(full_url)
            if etag:
                kwargs["lastmod"] = etag["date"]
            objs.append(SitemapURL(**kwargs))

    return objs


class SitemapURLManager(models.Manager):
    def refresh(self):
        with transaction.atomic(using=self.db):
            self.all().delete()
            self.bulk_create(get_sitemap_objs())

    def all_for_locale(self, locale):
        return self.filter(locale=locale).order_by('path')

    def all_locales(self):
        return self.values_list('locale', flat=True).distinct().order_by('locale')


class SitemapURL(models.Model):
    path = models.CharField(max_length=200)
    locale = models.CharField(max_length=5)
    lastmod = models.CharField(max_length=40, blank=True)

    objects = SitemapURLManager()

    def __str__(self):
        if self.locale:
            return f'/{self.locale}{self.path}'
        else:
            return self.path

    def get_absolute_url(self):
        return f'{settings.CANONICAL_URL}{self}'
