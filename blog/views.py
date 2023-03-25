from django.shortcuts import render, get_object_or_404
from .models import Post,Comment
from django.http import Http404
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm,CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

# Create your views here.
'''def post_list(request):
    posts_list = Post.published.all()

    #making a pagination that returns 3 posts per page
    paginator = Paginator(posts_list, 3)
    page_number = request.GET.get('page',1)

    #handling errors in the case of out of range numbers and alphabets
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html',{'posts': posts})'''

#creating a class based view as opposed to the function based view 
class PostListView(ListView):
    """
    An alternative lsit view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year,month,day,post):
    try:
        post = get_object_or_404(Post,status = Post.Status.PUBLISHED, 
                                 slug = post,
                                 publish__year = year,
                                 publish__month = month,
                                 publish__day = day)
    except Post.DoesNotExist:
        raise Http404('No Post Found')
    #display comments
    comments = post.comments.filter(active = True)

    #form to allow users to add comments 
    form = CommentForm()
    
    return render(request, 'blog/post/detail.html', {'post':post,'comments':comments,'form':form})

def post_share(request, post_id):
     post = get_object_or_404(Post, id = post_id, status = Post.Status.PUBLISHED)
     sent = False
     if request.method  == 'POST':
         form = EmailPostForm(request.POST)
         if form.is_valid():
             cd = form.cleaned_data
             post_url = request.build_absolute_uri(
             post.get_absolute_url())
             subject = f"{cd['name']} recommends you read " \
             f"{post.title}"
             message = f"Read {post.title} at {post_url}\n\n" \
             f"{cd['name']}\'s comments: {cd['comments']}"
             send_mail(subject, message, 'sagudze900@gmail.com',
             [cd['to']])
             sent = True
     else:
        form = EmailPostForm()
     return render(request, 'blog/post/share.html', {'post':post,'form':form,'sent':sent})

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id = post_id, status = Post.Status.PUBLISHED)
    comment = None

    form = CommentForm(data = request.POST)
    if form.is_valid():

        comment = form.save(commit = False)
        comment.post = post
        comment.save()

    return render(request, 'blog/post/comment.html', {'post':post,'form':form,'comment':comment})