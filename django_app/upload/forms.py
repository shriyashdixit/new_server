# forms.py
from django import forms

class SendMessageForm(forms.Form):
    chat_id = forms.CharField(max_length=255, label="Chat ID")
    message = forms.CharField(widget=forms.Textarea, label="Message")
