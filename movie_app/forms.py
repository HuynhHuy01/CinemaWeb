from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):

    RATING_CHOICES = [
    (5, "5 Stars"),
    (4, "4 Stars"),
    (3, "3 Stars"),
    (2, "2 Stars"),
    (1, "1 Star")
    ]
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.RadioSelect) 
    class Meta:
        model = Comment
        fields = ['content','rating']  

        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment here...',
                'required': 'required'
            }),
        }