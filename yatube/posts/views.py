from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import PostForm


posts_on_page = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, posts_on_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, posts_on_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user_name = get_object_or_404(User, username=username)
    paginator = Paginator(user_name.posts.all(), posts_on_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'user_name': user_name,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count_posts = Post.objects.all().filter(author__exact=post.author).count
    context = {
        'post': post,
        'count_posts': count_posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required()
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)  # записывает,но не сохраняет
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
    form = PostForm()
    return render(request, 'posts/post_create.html', {'form': form})


@login_required()
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post.id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'posts/post_create.html', context)
