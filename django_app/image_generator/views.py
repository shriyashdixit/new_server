# saas_service/views.py

from openai import OpenAI
from django.shortcuts import render
from .forms import ImageGenerationForm
from django.conf import settings
from django.contrib.auth.decorators import login_required

# Configure OpenAI API key
client = OpenAI()
client.api_key = settings.OPENAI_API_KEY


def generate_image_from_prompt(prompt):

    try:
        response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        )
        # Get the URL of the generated image
        image_url = response.data[0].url
        return image_url

    except Exception as e:
        print(f"Error generating image: {e}")
        return None

@login_required
def generate_image(request):
    generated_image_url = None

    if request.method == 'POST':
        form = ImageGenerationForm(request.POST)
        if form.is_valid():
            input_string = form.cleaned_data['input_string']
            generated_image_url = generate_image_from_prompt(input_string)

    else:
        form = ImageGenerationForm()

    return render(request, 'image_generator/generate_image.html', {'form': form, 'generated_image_url': generated_image_url})
