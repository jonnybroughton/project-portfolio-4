from django.contrib import admin
from .models import Post, Vote, Comment, UserProfile
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):

    list_display = ('title', 'slug', 'status', 'created_on')
    search_fields = ['title' , 'content']
    list_filter = ('status','created_on')
    prepopulated_fields = {'slug': ('title',)}
    summernote_fields = ('content',)

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'value',)
    search_fields = ['user__username', 'post__title']
    list_filter = ('value',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'favorite_car', 'current_car', 'post_count', 'comment_count')

# Register your models here.

admin.site.register(Comment)
admin.site.register(UserProfile, UserProfileAdmin)