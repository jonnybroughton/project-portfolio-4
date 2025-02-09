from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Vote, UserProfile
from .forms import CommentForm, PostForm, UserProfileForm


# Create your views here.
class PostList(generic.ListView):
    """
    View to list all posts.

    **Template:**

    :template:`news/index.html`
    """
    queryset = Post.objects.all().order_by("-created_on").filter(status=1)
    template_name = "news/index.html"
    paginate_by = 6


def post_detail(request, slug):
    """
    Display an individual :model:`news.Post`.

    **Context**

    ``post``
        An instance of :model:`news.Post`.

    **Template:**

    :template:`news/post_detail.html`
    """
    queryset = Post.objects.filter(status=1)
    post = get_object_or_404(queryset, slug=slug)
    comments = post.comments.all().order_by("-created_on")
    comment_count = post.comments.filter(approved=True).count()

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.comment_count += 1
            user_profile.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                'Comment submitted and awaiting approval'
            )

    comment_form = CommentForm()

    return render(
        request,
        "news/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_count": comment_count,
            "comment_form": comment_form,
        }
    )


@login_required
def create_post(request):
    """
    View to create a new post.

    **Context**

    ``form``
        An instance of :form:`PostForm`.

    **Template:**

    :template:`news/create_post.html`
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.post_count += 1
            user_profile.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                'Post created successfully and awaiting approval.'
            )
            return HttpResponseRedirect(reverse('home'))
    else:
        form = PostForm()

    return render(
        request,
        'news/create_post.html',
        {'form': form}
    )

def custom_403(request, exception):
    context = {'message': str(exception)}
    return render(request, 'news/templates/news/permission_denied.html', context, status=403)



@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if post.author != request.user:
        raise PermissionDenied("You are not authorized to edit this post.")
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                'Post updated successfully!'
            )
            return HttpResponseRedirect(reverse('post_detail', args=[post.slug]))
    else:
        form = PostForm(instance=post)

    return render(
        request,
        'news/edit_post.html',
        {'form': form, 'post': post}
    )



@login_required
def delete_post(request, slug):
    """
    View to delete a post.

    **Template:**

    Redirects to home if the post is deleted.
    """
    post = get_object_or_404(Post, slug=slug)

    if request.method == 'POST' and post.author == request.user:
        post.delete()
        user_profile = UserProfile.objects.get(user=post.author)
        if user_profile.post_count > 0:
            user_profile.post_count -= 1
            user_profile.save()
        messages.add_message(
            request,
            messages.SUCCESS,
            'Post deleted successfully!'
        )
        return HttpResponseRedirect(reverse('home'))

    return HttpResponseRedirect(reverse('post_detail', args=[slug]))


def comment_edit(request, slug, comment_id):
    """
    View to edit a comment.

    **Template:**

    Redirects to the post detail view after editing.
    """
    if request.method == "POST":
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comment = get_object_or_404(Comment, pk=comment_id)
        comment_form = CommentForm(data=request.POST, instance=comment)

        if comment_form.is_valid() and comment.author == request.user:
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.approved = False
            comment.save()
            messages.add_message(request, messages.SUCCESS, 'Comment Updated!')
        else:
            messages.add_message(request,
                                 messages.ERROR, 'Error updating comment!')

    return HttpResponseRedirect(reverse('post_detail', args=[slug]))


def comment_delete(request, slug, comment_id):
    """
    View to delete a comment.

    **Template:**

    Redirects to the post detail view after deletion.
    """
    print(f"Attempting to delete comment with ID {comment_id}")
    queryset = Post.objects.filter(status=1)
    post = get_object_or_404(queryset, slug=slug)
    comment = get_object_or_404(Comment, pk=comment_id)

    if comment.author == request.user:
        comment.delete()
        user_profile = UserProfile.objects.get(user=comment.author)
        if user_profile.comment_count > 0:
            user_profile.comment_count -= 1
            user_profile.save()
        messages.add_message(request, messages.SUCCESS, 'Comment deleted!')
    else:
        messages.add_message(
            request,
            messages.ERROR,
            'You can only delete your own comments!'
        )

    return HttpResponseRedirect(reverse('post_detail', args=[slug]))


@login_required
def vote_post(request, slug):
    """
    View to vote on a post.

    **Template:**

    Redirects to the post detail view after voting.
    """
    if request.method == 'POST':
        user = request.user
        post = get_object_or_404(Post, slug=slug)
        vote = post.votes.filter(user=user).first()

        if vote is not None:
            vote.delete()
        else:
            vote = Vote()
            vote.user = request.user
            vote.post = post
            vote.value = request.POST.get('vote_id')
            vote.save()
            print('VOTE: ', vote)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


@login_required
def profile_view(request):
    """
    View to display the user's profile.

    **Context**

    ``user_profile``
        An instance of :model:`UserProfile`.

    ``user_posts``
        A list of posts authored by the user.

    ``user_comments``
        A list of comments authored by the user.

    **Template:**

    :template:`news/profile.html`
    """
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)
    user_posts = Post.objects.filter(author=user,
                                     status=1).order_by("-created_on")
    user_comments = Comment.objects.filter(author=user).order_by("-created_on")

    context = {
        'user': user,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_comments': user_comments,
    }
    return render(request, 'news/profile.html', context)


@login_required
def edit_profile(request):
    """
    View to edit the user's profile.

    **Context**

    ``form``
        An instance of :form:`UserProfileForm`.

    **Template:**

    :template:`news/edit_profile.html`
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST,
                               request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(
        request,
        'news/edit_profile.html',
        {'form': form}
    )
