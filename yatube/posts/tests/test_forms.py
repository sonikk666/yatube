import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Comment

User = get_user_model()

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем группы и пользователя в базе данных
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.group_create = Group.objects.create(
            title='Группа при создании поста',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_edit = Group.objects.create(
            title='Группа при редактировании поста',
            slug='test-slug_2',
            description='Тестовое описание_2',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group_create,
            text='Пост для редактирования',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованый клиент автора поста
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_post_create(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        self.posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новый Тестовый текст',
            'group': self.group_create.id,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': 'TestAuthor'}
            )
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), self.posts_count + 1)

        # Проверяем, что создалась запись с заданным текстом
        self.create_post = Post.objects.latest('pub_date')

        self.assertEqual(
            self.create_post.text, form_data['text']
        )
        self.assertEqual(
            self.create_post.group.id, self.group_create.id
        )
        self.assertEqual(
            self.create_post.author.username, self.author.username
        )
        self.assertEqual(
            self.create_post.image, 'posts/small.gif'
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        # Подсчитаем количество записей в Post
        self.posts_count = Post.objects.count()
        small_gif_edit = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x01\x3B'
        )
        uploaded_edit = SimpleUploadedFile(
            name='small_edit.gif',
            content=small_gif_edit,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Редактированный пост',
            'group': self.group_edit.id,
            'image': uploaded_edit,
        }
        # Отправляем POST-запрос
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )
        # Проверяем, что число постов не увеличилось
        self.assertEqual(Post.objects.count(), self.posts_count)

        # Проверяем, что пост изменился
        self.edit_post = Post.objects.get(id=self.post.id)

        self.assertEqual(self.edit_post.text, form_data['text'])
        self.assertEqual(self.edit_post.group.id, self.group_edit.id)
        self.assertEqual(self.edit_post.author.username, self.author.username)
        self.assertEqual(self.edit_post.image, 'posts/small_edit.gif')


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commenter = User.objects.create_user(username='TestUser')
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.post_comment = Post.objects.create(
            author=cls.author,
            text='Пост для коммента',
        )
        cls.comment = Comment.objects.create(
            text='Комментарий',
            post=cls.post_comment,
            author=cls.commenter,
        )

    def setUp(self):
        # Создаем авторизованый клиент автора поста
        self.authorized_client = Client()
        self.authorized_client.force_login(self.commenter)

    def test_comment_create(self):
        """Валидная форма создает запись в Comment."""
        # Подсчитаем количество записей в Comment
        self.comments_count = Comment.objects.count()
        form_data = {
            'text': 'Новый Комментарий',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post_comment.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post_comment.id}
            )
        )
        # Проверяем, увеличилось ли число комментариев
        self.assertEqual(Comment.objects.count(), self.comments_count + 1)

        # Проверяем, что создалась запись с заданным текстом
        self.comment = Comment.objects.latest('created')

        self.assertEqual(
            self.comment.text, form_data['text']
        )
        self.assertEqual(
            self.comment.author.username, self.commenter.username
        )
