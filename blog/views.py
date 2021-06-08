from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import send_mail
from .models import Comment
from .forms import CommentForm, PostForm
# Create your views here.


def about(request):
    return render(request, 'blog/post/about.html')


def post_blog(request):
    posted = False
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            posted = True
    else:
        form = PostForm()
    return render(request, 'blog/post/post.html', {'form': form, 'posted': posted})


def post_share(request, post_id):
    # Retrieve post by id
     post = get_object_or_404(Post, id=post_id, status='published')
     sent = False
    #checking if form is valid and request method
     if request.method == 'POST':
         #Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Validation passed by forms
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'infotechupdatemedia@gmail.com', [cd['to']])
            sent = True
     else:
        form = EmailPostForm()
     return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 4
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month,
                             publish__day=day)
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create comment object but dont save it to database
            new_comment = comment_form.save(commit=False)
            # assign the curent post to the comment
            new_comment.post = post
            # save it to database
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post' : post,
                                                     'comments' : comments,
                                                     'new_comment': new_comment,
                                                     'comment_form' : comment_form})


# Notes
#  This is how pagination works:
# 1. We instantiate the Paginator class with the number of objects
#  we want to display on each page.
# 2. We get the page GET parameter that indicates the current page
# number.
# 3. We obtain the objects for the desired page calling the page()
# method of Paginator.
# 4. If the page parameter is not an integer, we retrieve the first
# page of results. If this parameter is a number higher than
# the last page of results, we will retrieve the last page.
# 5. We pass the page number and retrieved objects to the
# template.

