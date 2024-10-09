from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Vote
from .forms import CommentForm, PostForm


# Create your views here.
class PostList(generic.ListView):
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
            messages.add_message(
                request, messages.SUCCESS,
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
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  
            post.save()  
            messages.add_message(request, messages.SUCCESS, 'Post created successfully and awaiting approval.')
            return HttpResponseRedirect(reverse('home'))  
    else:
        form = PostForm()

    return render(request, 'news/create_post.html', {'form': form})

    
@login_required
def edit_post(request, slug):
    """
    View to edit a post
    """
    post = get_object_or_404(Post, slug=slug)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid() and post.author == request.user:
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Post updated successfully!')
            return HttpResponseRedirect(reverse('post_detail', args=[post.slug]))
    else:
        form = PostForm(instance=post)

    return render(request, 'news/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, slug):
    """
    View to delete a post
    """
    post = get_object_or_404(Post, slug=slug)

    if request.method == 'POST' and post.author == request.user:
        post.delete()
        messages.add_message(request, messages.SUCCESS, 'Post deleted successfully!')
        return HttpResponseRedirect(reverse('home'))  

    return HttpResponseRedirect(reverse('post_detail', args=[slug]))

def comment_edit(request, slug, comment_id):
    """
    view to edit comments
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
            messages.add_message(request, messages.ERROR, 'Error updating comment!')

    return HttpResponseRedirect(reverse('post_detail', args=[slug]))

def comment_delete(request, slug, comment_id):
    print(f"Attempting to delete comment with ID {comment_id}")
    """
    view to delete comment
    """
    queryset = Post.objects.filter(status=1)
    post = get_object_or_404(queryset, slug=slug)
    comment = get_object_or_404(Comment, pk=comment_id)

    if comment.author == request.user:
        comment.delete()
        messages.add_message(request, messages.SUCCESS, 'Comment deleted!')
    else:
        messages.add_message(request, messages.ERROR, 'You can only delete your own comments!')

    return HttpResponseRedirect(reverse('post_detail', args=[slug]))

@login_required
def vote_post(request, slug):
    # To run through this code when the user submits a vote
    if request.method == 'POST':

        # gets the user
        user = request.user

        # gets the current post
        post = get_object_or_404(Post, slug=slug)

        # filters the votes for the current post
        vote = post.votes.filter(user=user).first()

        if vote is not None:
            # if the vote already exists delete the vote
            vote.delete()
        else:
            # apply the submitted data to the Vote model
            vote = Vote()
            vote.user = request.user
            vote.post = post
            vote.value = request.POST.get('vote_id')
            vote.save()
            print('VOTE: ', vote)

        # return to the post_detail page
        return HttpResponseRedirect(reverse('post_detail', args=[slug]))

# @login_required
# def vote_post(request, slug, vote_value):
#     post = get_object_or_404(Post, slug=slug) # Retrieve the post by slug
#     vote = get_object_or_404(Vote, value=vote_value)

#     if request.method == 'POST':
#         try:

#             # vote_value = int(request.POST.get('vote_value', 0)) #Get the vote value from the request
#             print('VOTE: ', vote)
#             print(f"Vote value received: {vote_value}, {type(vote_value)}")

#             if vote_value not in [1, -1]:  # check if the vote value is valid
#                 return JsonResponse({'success': False, 'message': 'Invalid vote value.'}, status=400)

#             # try to get or create a vote object for the user and the post
#             vote, created = Vote.objects.get_or_create(user=request.user, post=post)
#             print(f"Vote created: {created}. Current Vote Value: {vote.value}")

#             if not created:
#                 print(f"User has already voted. Current Vote Value: {vote.value}, New Vote Value: {vote_value}")  
#                 if vote.value == vote_value:
#                     #if the vote value is the same as the current vote then remove it
#                     print("Vote value is the same as the current vote. Removing vote.")
#                     vote.delete()
#                     return JsonResponse({'success': True, 'message': 'Vote removed', 'total_votes': post.total_votes()})
#                 else:
#                     #if the vote is different then update the vote value
#                     print("Vote value is different. Updating vote value.")
#                     vote.value = vote_value
#                     vote.save() #save the vote value
#                     return JsonResponse({'success': True, 'message': 'Vote updated', 'total_votes': post.total_votes()})
#             else:
#                 #if the vote value doesnt exist then create a new vote
#                 print("Recording new vote.")
#                 vote.value = vote_value #assign the vote value
#                 vote.save() #save the new vote
#                 return JsonResponse({'success': True, 'message': 'Vote recorded', 'total_votes': post.total_votes()})

#         except ValueError as ve:
#             print(f"ValueError: {str(ve)}")  
#             return JsonResponse({'success': False, 'message': 'Invalid vote value.'}, status=400)
#         except Exception as e:
#             print(f"Error processing vote: {str(e)}")
#             return JsonResponse({'success': False, 'message': 'There was an error processing your vote.'}, status=400)

#     return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

