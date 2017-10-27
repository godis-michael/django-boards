from django import forms
from .models import Topic, Post


class NewTopicForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(), max_length=2500, help_text='The max length is 2500 symbols')

    class Meta:
        model = Topic
        fields = ['subject', 'message']


class PostReplyForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]