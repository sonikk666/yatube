"""Интерфейс администратора."""
from django.contrib import admin

from .models import Comment, Follow, Post, Group


class PostAdmin(admin.ModelAdmin):
    """Интерфейс постов."""
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
        'image',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Интерфейс групп."""
    list_display = (
        'title',
        'slug',
        'description',
    )
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    """Интерфейс комментариев."""
    list_display = (
        'pk',
        'post',
        'created',
        'author',
        'text',
    )
    list_filter = ('created',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """Интерфейс полписок."""
    list_display = (
        'author',
        'user',
    )
    list_filter = ('author', 'user',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Comment, CommentAdmin)
