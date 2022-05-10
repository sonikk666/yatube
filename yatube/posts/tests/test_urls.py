from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestAuthorName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый пост',
        )
        cls.address_templates = (
            (reverse(
                'posts:index'
            ), 'OK', 'posts/index.html'),
            (reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ), 'OK', 'posts/group_list.html'),
            (reverse(
                'posts:profile', kwargs={'username': 'TestUsername'}
            ), 'OK', 'posts/profile.html'),
            (reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id}
            ), 'OK', 'posts/post_detail.html'),
            (reverse(
                'posts:post_create'
            ), 'Found', 'posts/create_post.html'),
            (reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.id}
            ), 'Found', 'posts/create_post.html'),
            # Несуществующая страница - 404 - кастомный шаблон
            ('/unexisting_page/', 'Not Found', 'core/404.html'),
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент пользователя
        self.user = User.objects.create_user(username='TestUsername')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем авторизованный клиент автора
        self.author_client = Client()
        self.author_client.force_login(self.author)

    # Проверяем общедоступные страницы
    def test_guest_url_exists_at_desired_location(self):
        """Страницы, доступные любому пользователю."""
        for address, reason_phrase, _ in self.address_templates:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.reason_phrase, reason_phrase)

    def test_post_create_url_exists_at_desired_location(self):
        """Страница создания поста доступна авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        self.assertEqual(response.reason_phrase, 'OK')

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница редактирования поста доступна автору."""
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.reason_phrase, 'OK')

    def test_add_comment_url_exists_at_desired_location(self):
        """
        Страница создания комментария
        доступна авторизованному пользователю.
        """
        response = self.author_client.get(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.reason_phrase, 'Found')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, _, template in self.address_templates:
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
