from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from django.core.paginator import Paginator
import datetime
from django.views.generic.base import TemplateView
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .forms import PostForm


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user_name = get_object_or_404(User, username=username)
    post_list1 = Post.objects.all().filter(author__exact=user_name)
    post_list = post_list1.order_by('-pub_date')
    count_posts = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'user_name': user_name,
        'post_list': post_list,
        'count_posts': count_posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count_posts = Post.objects.all().filter(author__exact=post.author).count
    title = 'Пост'
    context = {
        'title': title,
        'post': post,
        'count_posts': count_posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required()
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            group = form.cleaned_data['group']
            post = form.save(commit=False)  # записывает,но не сохраняет
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
    form = PostForm()
    return render(request, 'posts/post_create.html', {'form': form})


@login_required()
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)
    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(request.POST or None, instance=post)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'posts/post_create.html', context)
