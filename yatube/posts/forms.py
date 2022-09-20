from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = {
            'text': 'Текст поста',
            'group': 'Группы',
            'image': 'Картинка',
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'card'}),
            'group': forms.Select(attrs={'class': 'card'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

        fields = {
            'text': 'Текст комментария'
        }
