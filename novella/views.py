from django.shortcuts import render, get_object_or_404
from django.views import generic, View
from .models import Post, Category, Profile
from .forms import CommentForm
from django.urls import reverse


# Create your views here.
# def home(request):
#     return render(request, 'index.html')
class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by("-created_on")
    template_name = "story/index.html"
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        cat_list = Category.objects.all()
        context = super(PostList, self).get_context_data(*args, **kwargs)
        context["cat_list"] = cat_list
        return context


class ViewStory(View):

    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.all().order_by("-created_on")

        return render(
            request,
            "story/view_post.html",
            {
                "post": post,
                "comments": comments,
                "comment_form": CommentForm()
            },
        )

    def post(self, request, slug, *args, **kwargs):

        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.all().order_by("-created_on")

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
        else:
            comment_form = CommentForm()

        return render(
            request,
            "story/view_post.html",
            {
                "post": post,
                "comments": comments,
                "comment_form": comment_form,
            },
        )


class ProfilePublic(generic.ListView):
    """View for the profiles of authors of posts.
    this can be viewd by clicking on post title and author headings
    login is required"""
    model = Post
    paginate_by = 7
    context_object_name = 'posts'
    template_name = 'story/profile_public.html'

    def get_queryset(self):
        author_id = self.kwargs['pk']
        return Post.objects.filter(author=author_id, status=1).order_by("-created_on")

    def get_context_data(self, *args, **kwargs):
        user_id = self.kwargs['pk']
        queryset = Profile.objects.filter(id=user_id)
        author = get_object_or_404(queryset)
        context = super(ProfilePublic, self).get_context_data(*args, **kwargs)
        context["author"] = author
        return context


# class ViewProfilePrivate(generic.ListView):
#     model = Post
#     paginate_by = 7
#     context_object_name = 'posts'
#     template_name = 'story/profile_private.html'

#     def get_queryset(self):
#         user_id = self.kwargs['pk']
#         return Post.objects.filter(author=user_id).order_by("-created_on")

#     def get_context_data(self, *args, **kwargs):
#         user_id = self.kwargs['pk']
#         queryset = Profile.objects.filter(id=user_id)
#         author = get_object_or_404(queryset)
#         context = super(ViewProfilePrivate, self).get_context_data(*args, **kwargs)
#         context["user"] = user
#         return context

class ProfilePrivate(View):

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['id']
        queryset = Profile.objects.filter(id=user_id)
        profile = get_object_or_404(queryset)
        posts = Post.objects.filter(author=user_id)

        return render(request, 'story/profile_private.html', {
            "profile": profile,
            "posts": posts
        })


def CategoryView(request, category):
    post_cat = Post.objects.filter(category=category)
    return render(request, 'story/category.html', {'category': category, 'post_cat': post_cat})


class AddArticle(generic.CreateView):
    model = Post
    template_name = 'story/add_post.html'
    fields = [
        'title',
        'slug',
        'author',
        'category',
        'content',
        'featured_image',
        'excerpt',
        'status'
        ]
