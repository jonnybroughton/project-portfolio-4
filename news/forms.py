from .models import Comment, Post, UserProfile
from django import forms
from cloudinary.forms import CloudinaryFileField
from django_summernote.widgets import SummernoteWidget

# ==============================
# Form: CommentForm
# ==============================
class CommentForm(forms.ModelForm):
    """Form for submitting comments on posts."""
    class Meta:
        model = Comment
        fields = ('body',)

# ==============================
# Form: PostForm
# ==============================
class PostForm(forms.ModelForm):
    """Form for creating and editing blog posts."""
    class Meta:
        model = Post
        fields = ['title', 'featured_image', 'content', 'excerpt']
        widgets = {
            'content': SummernoteWidget(),
        }

    def save(self, commit=True):
        """Override save method to customize post saving behavior."""
        post = super().save(commit=False)
        if commit:
            post.save()
        return post

# ==============================
# Form: UserProfileForm
# ==============================
class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""
    profile_picture = CloudinaryFileField(required=False)

    class Meta:
        model = UserProfile
        fields = ['favorite_car', 'current_car', 'profile_picture']
