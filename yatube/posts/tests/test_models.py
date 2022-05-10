from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()

CHAR_AMOUNT = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост' * 3,
            author=cls.author,
        )

    def test_model_group_have_correct_group_name(self):
        """Проверяем, что у моделей корректно работает __str__ группы."""
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(self.group))

    def test_model_post_have_correct_post_text(self):
        """Проверяем, что у моделей корректно работает __str__ поста."""
        expected_object_name = self.post.text[:CHAR_AMOUNT]
        self.assertEqual(expected_object_name, str(self.post))

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                response = self.post._meta.get_field(value).help_text
                self.assertEqual(response, expected)
