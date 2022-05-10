from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    """Форма для новой записи, на основе модели Post."""
    class Meta:
        model = Post
        # Поля модели, которые должны отображаться в веб-форме
        fields = ('text', 'group', 'image')
        # labels = {
        #     'text': 'Текст поста',
        #     'group': 'Название группы',
        # }
        # help_texts = {
        #     'text': 'Текст нового поста',
        #     'group': 'Группа, к которой будет относиться пост',
        # }


class CommentForm(ModelForm):
    """Форма для нового комментария, на основе модели Comment."""
    class Meta:
        model = Comment
        fields = ('text',)
