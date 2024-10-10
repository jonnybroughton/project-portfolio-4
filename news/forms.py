from .models import Comment, Post, UserProfile
from django import forms
from cloudinary.forms import CloudinaryFileField


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'featured_image', 'content', 'excerpt'] 

    def save(self, commit=True):
        post = super().save(commit=False)
        post.slug = '-'.join(post.title.lower().split())
        if commit:
            post.save()
        return post

class UserProfileForm(forms.ModelForm):
    profile_picture = CloudinaryFileField(required=False) 

    class Meta:
        model = UserProfile
        fields = ['favorite_car', 'current_car', 'profile_picture']