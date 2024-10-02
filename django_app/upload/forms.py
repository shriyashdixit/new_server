# forms.py
from django import forms
from .models import TelegramUser

class SendMessageForm(forms.Form):
    username = forms.ModelChoiceField(
        queryset=TelegramUser.objects.all(),
        label="Username",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label="Message"
    )
