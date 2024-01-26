from django.contrib import admin
from .models import *


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'body')
    # search_fields = ('id', 'title', 'topic')


@admin.register(Response)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_author_username', 'body', 'timestamp')

    def get_author_username(self, obj):
        return obj.user.username

    get_author_username.short_description = 'Author Username'
    get_author_username.admin_order_field = 'user__username'
