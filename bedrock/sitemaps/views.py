from django.views.generic import TemplateView

from bedrock.sitemaps.models import SitemapURL


class SitemapView(TemplateView):
    content_type = 'text/xml'

    def _get_locale(self):
        if self.kwargs['is_none']:
            locale = ''
        else:
            # can come back as empty string
            # should be None here if not a real locale
            locale = getattr(self.request, 'locale', None) or None

        return locale

    def get_template_names(self):
        if self._get_locale() is None:
            return ['sitemap_index.xml']
        else:
            return ['sitemap.xml']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        locale = self._get_locale()
        if locale is None:
            ctx['locales'] = SitemapURL.objects.all_locales()
        else:
            ctx['paths'] = SitemapURL.objects.all_for_locale(locale)

        return ctx
