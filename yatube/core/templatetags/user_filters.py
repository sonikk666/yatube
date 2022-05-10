from django import template

# Добавляем в template.Library наш фильтр
register = template.Library()


@register.filter
def addclass(field, css):
    """Фильтр, добавляющий CSS-класс в HTML-коде."""
    return field.as_widget(attrs={'class': css})
