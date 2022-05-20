from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

POST_COUNT: int = 10


def index(request):
    """Главная страница проекта Yatube."""
    posts = Post.objects.all()
    paginator = Paginator(posts, POST_COUNT)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    # Отдаем в словаре контекста
    context = {
        'page_obj': page_obj,
    }
    return render(
        request,
        'posts/index.html',
        context,
    )


def group_posts(request, slug):
    """Информация о группах проекта Yatube.
    Посты отфильтрованные по группе.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(
        request,
        'posts/group_list.html',
        context,
    )


def profile(request, username):
    """Страница профайла пользователя."""
    # Запрос к модели и создание словаря контекста
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    posts_count = posts.count()
    following = author.following.exists()
    following_count = author.following.all().count()
    follower_count = author.follower.all().count()

    context = {
        'page_obj': page_obj,
        'author': author,
        'posts_count': posts_count,
        'following': following,
        'following_count': following_count,
        'follower_count': follower_count,
    }
    return render(
        request,
        'posts/profile.html',
        context,
    )


def post_detail(request, post_id):
    """Страница отдельного поста."""
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    posts_count = author.posts.count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    following_count = author.following.all().count()
    follower_count = author.follower.all().count()
    context = {
        'post': post,
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
        'following_count': following_count,
        'follower_count': follower_count,
    }
    return render(
        request,
        'posts/post_detail.html',
        context,
    )


@login_required
def post_edit(request, post_id):
    """Страница редактирования поста."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    context = {
        'form': form,
        'is_edit': True,
    }
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id=post.pk)
    return render(request, 'posts/create_post.html', context)


@login_required
def post_create(request):
    """Страница создания нового поста."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def add_comment(request, post_id):
    """Создание нового комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post.pk)


@login_required
def follow_index(request):
    """Страница подписок пользователя."""
    posts = (
        Post.objects.select_related()
        .filter(author__following__user=request.user)
    )
    paginator = Paginator(posts, POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(
        request,
        'posts/follow.html',
        context,
    )


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    user = request.user
    author = get_object_or_404(User, username=username)
    is_exist = Follow.objects.filter(user=user, author=author).exists()
    if user != author and not is_exist:
        Follow.objects.create(user=user, author=author)
    return redirect(
        'posts:profile',
        username=username
    )


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора."""
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect(
        'posts:profile',
        username=username
    )
