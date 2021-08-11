from django.forms import ModelForm, Textarea

from .models import Comment, Post


class PostForm(ModelForm):
    """Форма для создания постов."""
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        help_texts = {
            'text': 'Текст поста',
            'group': 'Группа поста',
            'image': 'Загрузить изображение',
        }


class CommentForm(ModelForm):
    """Форма для создания комментариев."""
    class Meta:
        model = Comment
        fields = ['text']
        help_texts = {
            'text': 'Комментарий',
        }
        widgets = {
            'text': Textarea(attrs={'rows': 5}),
        }
