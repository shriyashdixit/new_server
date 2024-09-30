from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from .models import TelegramMessage  # Your model to save messages
import json
from .models import TelegramMessage
from datetime import datetime
from .utils import send_telegram_message
from .forms import SendMessageForm
from django.contrib.auth.decorators import login_required
# Create your views here.


def image_upload(request):
    if request.method == "POST" and request.FILES["image_file"]:
        image_file = request.FILES["image_file"]
        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        image_url = fs.url(filename)
        print(image_url)
        return render(request, "upload.html", {
            "image_url": image_url
        })
    return render(request, "upload.html")


def chatbot(request):
    return render(request, 'chatbot.html')


def env(request):
    return render(request, 'temporary_webpage.html')


def e_commerce(request):
    return render(request, 'e_commerce.html')


def tutorials_webpage(request):
    return render(request, 'tutorials_webpage.html')


def test(request):
    return render(request, 'homepage_main.html')

def homepage_main(request):
    folder1_path = os.path.join(settings.STATIC_ROOT, 'folder1')
    folder2_path = os.path.join(settings.STATIC_ROOT, 'folder2')

    images_folder1 = [f'folder1/{img}' for img in os.listdir(folder1_path) if img.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    images_folder2 = [f'folder2/{img}' for img in os.listdir(folder2_path) if img.endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    return render(request, 'test.html', {
        'images_folder1': images_folder1,
        'images_folder2': images_folder2
    })


@csrf_exempt
def save_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data
            print(message)
            TelegramMessage.objects.create(
                chat_id=data.get('chat_id'),
                message_id=data.get('message_id'),
                user_id=data.get('user_id'),
                username=data.get('username'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                message_text=data.get('message_text'),
                date_sent=datetime.fromisoformat(data.get('date_sent')),
                is_bot=data.get('is_bot'),
                chat_type=data.get('chat_type'),
                reply_to_message_id=data.get('reply_to_message_id'),
            )
            return JsonResponse({'status': 'success', 'message': 'Message saved successfully'})
        except Exception as e:
            print("error", e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def trigger_view(request):
    # Example: Check if a database entry has been updated or created
    CHAT_ID = ""
    # Send a Telegram message when the condition is met
    send_telegram_message(f"A database entry has triggered an event: {CHAT_ID}", CHAT_ID)

    return render(request, 'your_template.html', {'instance': CHAT_ID})

@login_required
@csrf_exempt  # Exempt this view from CSRF check for external services
def send_message_view(request):
    if request.method == 'POST':
        form = SendMessageForm(request.POST)
        if form.is_valid():
            chat_id = form.cleaned_data['chat_id']
            message = form.cleaned_data['message']

            # Trigger the function to send the message
            response = send_telegram_message(message, chat_id)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Message sent successfully',
                'response': response
            })
    else:
        form = SendMessageForm()

    return render(request, 'send_message.html', {'form': form})
