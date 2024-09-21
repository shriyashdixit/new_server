from django import forms

class ImageGenerationForm(forms.Form):
    input_string = forms.CharField(label='Input String', max_length=1000, widget=forms.TextInput(attrs={'placeholder': 'Enter a string...'}))