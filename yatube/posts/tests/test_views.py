from django.core.cache import cache
import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Group, Post, Comment, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

POSTS_COUNT = 1
POSTS_FOLLOW_COUNT = 1


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class MyViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.author = User.objects.create_user(username='TestAuthorName')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа_1',
            slug='test-slug_1',
            description='Тестовое описание_1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug_2',
            description='Тестовое описание_2',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group_1,
            text='Тестовый пост',
            image=cls.uploaded,
        )
        cls.commenter = User.objects.create_user(username='TestCommenter')
        cls.comments = Comment.objects.create(
            post=cls.post,
            author=cls.commenter,
            text='Комментарий',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованый клиент автора
        self.author_client = Client()
        self.author_client.force_login(self.author)


class PostPagesTest(MyViewsTest):
    def test_pages_uses_correct_template(self):
        """Name URL-адреса использует соответствующий шаблон."""
        # Собираем в словарь пары "reverse(name): имя_html_шаблона"
        templates_page_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug_1'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'TestAuthorName'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_post(self):
        """Проверка наличия поста и всех полей из контекста."""
        list_urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug_1'}),
            reverse('posts:profile', kwargs={'username': 'TestAuthorName'}),
        )
        for url_path in list_urls:
            with self.subTest(url_path=url_path):
                response = self.client.get(url_path)
                first_object = response.context['page_obj'][0]

                templates_context_fields = {
                    first_object: self.post,
                    first_object.text: self.post.text,
                    first_object.author.username: self.author.username,
                    first_object.group.title: self.group_1.title,
                    first_object.group.slug: self.group_1.slug,
                    first_object.group.description: self.group_1.description,
                    first_object.image: self.post.image,
                }

                for context_fields, value in templates_context_fields.items():
                    with self.subTest(context_fields=context_fields):
                        self.assertEqual(context_fields, value)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context['post'].text, 'Тестовый пост')
        self.assertEqual(response.context['posts_count'], POSTS_COUNT)
        self.assertEqual(response.context['post'].image, self.post.image)
        # Проверка формы и контекста комментария
        self.assertIsInstance(
            response.context['form'].fields['text'],
            forms.fields.CharField
        )
        self.assertEqual(response.context['post'].comments, self.post.comments)

    def test_create_edit_pages_show_correct_context(self):
        """Шаблон create и edit сформирован с правильным контекстом."""

        list_urls = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        )
        for path in list_urls:
            response = self.author_client.get(path)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field_create = response.context['form'].fields[value]
                self.assertIsInstance(form_field_create, expected)

        self.assertTrue(
            self.author_client.get(list_urls[1]).context['is_edit']
        )

    def test_correct_group_post(self):
        """Появление нового поста в нужной группе."""
        # Пара - URl_adress: количество постов
        templates_create_new = {
            reverse(
                'posts:index'
            ): POSTS_COUNT,
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug_1'}
            ): POSTS_COUNT,
            reverse(
                'posts:profile', kwargs={'username': 'TestAuthorName'}
            ): POSTS_COUNT,
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug_2'}
            ): 0,
        }
        for url_path, count in templates_create_new.items():
            with self.subTest(url_path=url_path):
                response = self.client.get(url_path)
                self.assertContains(response, self.post.text, count)

    def test_comment_create_login_required(self):
        """Неавторизованный пользователь не может комментировать."""
        response = self.client.get(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id})
        )
        self.assertRedirects(
            response,
            f'{reverse("users:login")}?next='
            f'{reverse("posts:add_comment", kwargs={"post_id": self.post.id})}'
        )

    def test_cache_index_page(self):
        """Кеширование главной страницы."""
        Post.objects.create(
            author=self.author,
            text='Пост для удаления',
        )
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        cache_check = response.content
        post = Post.objects.latest('pub_date')
        post.delete()
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(response.content, cache_check)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, cache_check)


class PaginatorViewsTest(MyViewsTest):
    def test_pages_contains_count_of_records(self):
        """Cтраницы содержат нужное количетсво записей."""
        # Здесь создаются ещё 12 тестовых записей.
        for post_number in range(12):
            self.post = Post.objects.create(
                author=self.author,
                group=self.group_1,
                text=f'Тестовый пост_{post_number}',
            )
        POSTS_ON_PAGE_1 = 10
        POSTS_ON_PAGE_2 = 3

        url_for_paginator = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug_1'}),
            reverse('posts:profile', kwargs={'username': 'TestAuthorName'}),
        )
        pages_paginator = (
            (1, POSTS_ON_PAGE_1),
            (2, POSTS_ON_PAGE_2),
        )
        for url_path in url_for_paginator:
            for page_number, posts_count in pages_paginator:
                with self.subTest(url_path=url_path, page=page_number):
                    response = self.client.get(
                        url_path, {'page': page_number}
                    ).context['page_obj']

                    self.assertEqual(len(response), posts_count)


class FollowsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.no_follower = User.objects.create_user(username='TestNoFollower')
        cls.follower = User.objects.create_user(username='TestFollower')
        cls.author_new = User.objects.create_user(username='TestAuthorNameNew')
        cls.post_new = Post.objects.create(
            author=cls.author_new,
            text='Тестовый пост_new',
        )
        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.author_new,
        )

    def setUp(self):
        # Создаем авторизованый клиент
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.no_follower_client = Client()
        self.no_follower_client.force_login(self.no_follower)


    def test_pages_follows_uses_correct_template(self):
        """URL-адрес follow_index использует соответствующий шаблон."""
        response = self.follower_client.get(
            reverse('posts:follow_index')
        )
        self.assertTemplateUsed(response, 'posts/follow.html')

    def test_context_post_follow(self):
        """"Шаблон follow_index сформирован с правильным контекстом."""
        response = self.follower_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]

        templates_context_fields = {
            first_object: self.post_new,
            first_object.text: self.post_new.text,
            first_object.author.username: self.author_new.username,
        }

        for context_fields, value in templates_context_fields.items():
            with self.subTest(context_fields=context_fields):
                self.assertEqual(context_fields, value)

    def test_follower(self):
        """Появление нового поста в ленте подписчика."""
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertContains(response, self.post_new.text, POSTS_FOLLOW_COUNT)

    def test_no_follower(self):
        """Новый пост в ленте не_подписанного не появился."""
        response = self.no_follower_client.get(reverse('posts:follow_index'))
        self.assertNotContains(response, self.post_new.text)

    def test_profile_follow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей."""
        # Подписываемся на автора
        self.no_follower_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'TestAuthorNameNew'})
        )
        response = self.no_follower_client.get(reverse('posts:follow_index'))
        self.assertIn(self.post_new, response.context['page_obj'])
       
    def test_profile_unfollow(self):
        """Авторизованный пользователь может
        удалять из подписок других пользователей."""
        # Отписываемся от автора
        self.no_follower_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'TestAuthorNameNew'})
        )
        response = self.no_follower_client.get(reverse('posts:follow_index'))
        self.assertNotIn(self.post_new, response.context['page_obj'])
