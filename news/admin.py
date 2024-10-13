from django.contrib import admin
from .models import Post, Vote, Comment, UserProfile
from django_summernote.admin import SummernoteModelAdmin

# ==============================
# Admin: PostAdmin
# ==============================


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    """Admin interface for managing blog posts."""

    list_display = ('title', 'slug', 'status', 'created_on')
    search_fields = ['title', 'content']
    list_filter = ('status', 'created_on')
    summernote_fields = ('content',)


# ==============================
# Admin: VoteAdmin
# ==============================
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Admin interface for managing votes on posts."""

    list_display = ('user', 'post', 'value',)
    search_fields = ['user__username', 'post__title']
    list_filter = ('value',)


# ==============================
# Admin: UserProfileAdmin
# ==============================
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for managing user profiles."""

    list_display = ('user', 'favorite_car', 'current_car',
                    'post_count', 'comment_count')


# Register the Comment model with the default admin options.
admin.site.register(Comment)

# Register the UserProfileAdmin with the UserProfile model.
admin.site.register(UserProfile, UserProfileAdmin)
