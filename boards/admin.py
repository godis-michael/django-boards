from django.contrib import admin
from .models import Board, Topic, Post


class PostInline(admin.StackedInline):
    model = Post
    extra = 3


class TopicAdmin(admin.ModelAdmin):
    inlines = [PostInline]


admin.site.register(Board)
admin.site.register(Topic, TopicAdmin)