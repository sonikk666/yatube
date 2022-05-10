from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Статичная страница 'Об авторе'."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Статичная страница 'Технологии'."""
    template_name = 'about/tech.html'
