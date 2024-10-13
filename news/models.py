from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils.text import slugify
import re

# Define the status choices for posts
STATUS = ((0, "Draft"), (1, "Published"))

# ==============================
# Model: Post
# ==============================


class Post(models.Model):
    """Model representing a blog post."""
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="news_posts")
    featured_image = CloudinaryField('image', default='placeholder')
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=0)
    excerpt = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return f"{self.title} | written by {self.author}"

    def total_upvotes(self):
        return self.votes.filter(value=1).count()

    def total_downvotes(self):
        return self.votes.filter(value=-1).count()

    def total_votes(self):
        return self.total_upvotes() - self.total_downvotes()

    def save(self, *args, **kwargs):
        """Override save method to generate a unique slug."""
        if not self.slug:
            slug = slugify(self.title)
            slug = slug.replace(':', '-')
            slug = re.sub(r'[^a-zA-Z0-9_-]', '-', slug)

            unique_slug = slug
            num = 1
            while Post.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{slug}-{num}'
                num += 1

            self.slug = unique_slug
        super().save(*args, **kwargs)

# ==============================
# Model: Vote
# ==============================


class Vote(models.Model):
    """Model representing a vote on a post."""
    VOTE_CHOICES = (
        (1, 'Upvote'),
        (-1, 'Downvote'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user_votes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='votes')
    value = models.IntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} voted {self.value} on {self.post.title}"

# ==============================
# Model: Comment
# ==============================


class Comment(models.Model):
    """Model representing a comment on a post."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="commenter")
    body = models.TextField()
    approved = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return f"Comment {self.body} by {self.author}"

# ==============================
# Model: UserProfile
# ==============================


class UserProfile(models.Model):
    """Model representing a user's profile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_car = models.CharField(max_length=100)
    current_car = models.CharField(max_length=100)
    post_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    profile_picture = CloudinaryField('image', null=True, blank=True)

    def __str__(self):
        return self.user.username