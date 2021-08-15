from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.select_related('author', 'group').all()
    paginator = Paginator(post_list, settings.MAX_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/index.html',
        {'page': page, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related(
        'group',
        'author'
    ).filter(group=group).all()
    paginator = Paginator(posts, settings.MAX_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page': page,
    }
    return render(request, 'posts/group.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related(
        'author', 'group'
    ).filter(author=author).all()
    followers = Follow.objects.filter(author=author.id).count()
    follows = Follow.objects.filter(user=author.id).count()
    following = Follow.objects.filter(
        user=request.user.id,
        author=author.id
    ).all()
    paginator = Paginator(posts, settings.MAX_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'author': author,
        'posts': posts,
        'followers': followers,
        'follows': follows,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'author': author,
        'posts': posts,
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    form = PostForm()
    context = {'form': form}
    return render(request, 'posts/new_post.html', context)


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(f'/{username}/{post_id}/')
    form = PostForm(instance=post)
    context = {
        'author': author,
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/new_post.html', context)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(f'/{username}/{post_id}/')
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'posts/comments.html', context)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related('author', 'group')
    paginator = Paginator(posts, settings.MAX_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow_check = Follow.objects.filter(user=user, author=author).exists()
    if author != user and not follow_check:
        Follow.objects.create(user=user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow_check = Follow.objects.filter(user=user, author=author).exists()
    if request.user != author and follow_check:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
