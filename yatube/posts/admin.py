from django.contrib import admin

from .models import Follow, Group, Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
        'image',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = ('-пусто-')


admin.site.register(Group)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'text',
        'created',
        'author',
    )
    empty_value_display = ('-пусто-')


@admin.register(Follow)
class FllowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
