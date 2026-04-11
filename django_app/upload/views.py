from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
import requests
import threading
import queue
from django.conf import settings
from django.contrib import messages
# views.py
from django.http import JsonResponse, StreamingHttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
# from .models import TelegramMessage  # Your model to save messages
import json
from .models import TelegramMessage, TelegramUser, ContactSubmission
from datetime import datetime
from .utils import send_telegram_message_to_chat, send_telegram_message, notify_landing_page_visit
from .forms import SendMessageForm
from django.contrib.auth.decorators import login_required
# Create your views here.


def error_404(request, exception=None):
    return render(request, '404.html', status=404)


def error_500(request):
    return render(request, '500.html', status=500)

LLM_URL = getattr(settings, "LLM_SERVER_URL", "http://llm:8080")

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
    notify_landing_page_visit(request)

    folder1_path = os.path.join(settings.STATIC_ROOT, 'folder1')
    folder2_path = os.path.join(settings.STATIC_ROOT, 'folder2')

    images_folder1 = [
        f'folder1/{img}'
        for img in os.listdir(folder1_path)
        if img.endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ]
    images_folder2 = [
        f'folder2/{img}'
        for img in os.listdir(folder2_path)
        if img.endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ]

    return render(request, 'homepage_main.html', {
        'images_folder1': images_folder1,
        'images_folder2': images_folder2,
    })


def services_page(request):
    return render(request, 'services.html')


def skills_page(request):
    return render(request, 'skills.html')


def work_page(request):
    return render(request, 'work.html')


def team_page(request):
    return render(request, 'team.html')


def culture_page(request):
    return render(request, 'culture.html')


def careers_page(request):
    return render(request, 'careers.html')


def blogs_page(request):
    return render(request, 'blogs.html')


def contact_page(request):
    if request.method == 'POST':
        # Extract all data first so we can log bot attempts too
        raw_ip = (
            request.META.get('HTTP_X_FORWARDED_FOR', '')
            .split(',')[0].strip()
            or request.META.get('REMOTE_ADDR', '')
        )
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        company = request.POST.get('company', '').strip()
        service = request.POST.get('service', '').strip()
        message = request.POST.get('message', '').strip()
        is_bot = bool(request.POST.get('website', ''))  # honeypot field

        # Rate limit real users only (bots bypass silently)
        if not is_bot:
            from django.core.cache import cache
            rate_key = f'contact_rate_{raw_ip}'
            submit_count = cache.get(rate_key, 0)
            if submit_count >= 5:
                return render(request, 'contact.html', {'rate_limited': True})
            cache.set(rate_key, submit_count + 1, timeout=3600)

        if name and email:
            # Save immediately with basic data; background thread adds geo
            submission = ContactSubmission.objects.create(
                name=name, email=email, phone=phone,
                company=company, service=service, message=message,
                ip_address=raw_ip or None,
                is_bot=is_bot,
            )

            import threading

            def _enrich_and_notify(sub_id, raw_ip, chat_id, is_bot):
                try:
                    from upload.utils import get_ip_location, get_reverse_dns, get_abuse_score, update_ip_record
                    from upload.models import ContactSubmission as CS
                    from datetime import datetime, timezone, timedelta

                    geo = get_ip_location(raw_ip)
                    hostname = get_reverse_dns(raw_ip)
                    abuse_score, abuse_reports = get_abuse_score(raw_ip)

                    CS.objects.filter(pk=sub_id).update(
                        city=geo.get('city', ''),
                        region=geo.get('regionName', ''),
                        country=geo.get('country', ''),
                        isp=geo.get('isp', ''),
                    )
                    update_ip_record(
                        raw_ip, geo=geo,
                        form_submitted=not is_bot,
                        is_bot=is_bot,
                        hostname=hostname,
                        abuse_score=abuse_score,
                        abuse_total_reports=abuse_reports,
                    )

                    if chat_id:
                        IST = timezone(timedelta(hours=5, minutes=30))
                        ts = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')
                        city = geo.get('city', '?')
                        region = geo.get('regionName', '?')
                        country = geo.get('country', '?')
                        isp = geo.get('isp', '?')
                        status_line = (
                            '🤖 <b>BOT SUBMISSION DETECTED</b>'
                            if is_bot else
                            '✅ <b>New Contact Form Submission</b>'
                        )
                        abuse_line = (
                            f'⚠️ <b>Abuse Score:</b> {abuse_score}% ({abuse_reports} reports)\n'
                            if abuse_score is not None else ''
                        )
                        hostname_line = f'🖥 <b>Hostname:</b> {hostname}\n' if hostname else ''
                        msg = (
                            f'{status_line}\n\n'
                            f'🕒 <b>Time:</b> {ts}\n'
                            f'👤 <b>Name:</b> {name}\n'
                            f'📧 <b>Email:</b> {email}\n'
                            f'📞 <b>Phone:</b> {phone or "—"}\n'
                            f'🏢 <b>Company:</b> {company or "—"}\n'
                            f'🔧 <b>Service:</b> {service or "—"}\n'
                            f'💬 <b>Message:</b>\n{message}\n\n'
                            f'🌍 <b>IP:</b> {raw_ip}\n'
                            f'{hostname_line}'
                            f'📍 <b>Location:</b> {city}, {region}, {country}\n'
                            f'📡 <b>ISP:</b> {isp}\n'
                            f'{abuse_line}'
                        )
                        send_telegram_message(chat_id, msg)
                except Exception:
                    pass

            threading.Thread(
                target=_enrich_and_notify,
                args=(submission.pk, raw_ip, settings.TELEGRAM_CHAT_ID, is_bot),
                daemon=True,
            ).start()

        from django.shortcuts import redirect
        return redirect('/contact/?sent=1')

    sent = request.GET.get('sent') == '1'
    return render(request, 'contact.html', {'sent': sent})


@csrf_exempt
def save_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            username = data.get('username')
            chat_id = data.get('chat_id')

            # Step 1 & 3: Check if the user entry exists, if not, create it.
            user, created = TelegramUser.objects.get_or_create(
                user_id=user_id,
                username=username,
                defaults={'chat_id': chat_id}
            )

            # Step 2: If the entry exists but the chat_id doesn't match, update it.
            if not created and user.chat_id != chat_id:
                user.chat_id = chat_id
                user.save()

            TelegramMessage.objects.create(
                chat_id=chat_id,
                message_id=data.get('message_id'),
                user_id=user_id,
                username=username,
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
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def trigger_view(request):
    # Example: Check if a database entry has been updated or created
    CHAT_ID = ""
    # Send a Telegram message when the condition is met
    send_telegram_message_to_chat(f"A database entry has triggered an event: {CHAT_ID}", CHAT_ID)

    return render(request, 'your_template.html', {'instance': CHAT_ID})

@login_required
@csrf_exempt
def send_message_view(request):
    if request.method == 'POST':
        form = SendMessageForm(request.POST)
        if form.is_valid():
            telegram_user = form.cleaned_data['username']
            message = form.cleaned_data['message']
            chat_id = telegram_user.chat_id

            # Trigger the function to send the message
            response = send_telegram_message(chat_id, message)
            
            if response.get('status') == 'success':
                messages.success(request, 'Message sent successfully.')
            else:
                messages.error(request, 'Failed to send the message.')
    else:
        form = SendMessageForm()
    
    return render(request, 'send_message.html', {'form': form})

@csrf_exempt
def chat_stream(request):
    qtxt = request.GET.get("q", "").strip()
    if not qtxt:
        return HttpResponseBadRequest("q required")

    def gen():
        buf: queue.Queue[bytes | object] = queue.Queue(maxsize=256)
        STOP = object()

        def reader():
            try:
                with requests.post(
                    f"{LLM_URL}/v1/chat/completions",
                    json={
                        "model": "mistral",
                        "messages": [{"role": "user", "content": qtxt}],
                        "stream": True,
                    },
                    stream=True, timeout=None,
                ) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            buf.put(chunk)
            finally:
                buf.put(STOP)

        threading.Thread(target=reader, daemon=True).start()

        while True:
            try:
                chunk = buf.get(timeout=5)  # heartbeat every 5s if idle
                if chunk is STOP:
                    yield b"data: [DONE]\n\n"
                    break
                yield chunk
            except queue.Empty:
                # keep the HTTP connection alive
                yield b":keepalive\n\n"

    response = StreamingHttpResponse(gen(), content_type="text/event-stream; charset=utf-8")
    # important for proxies/servers
    response["Cache-Control"] = "no-cache, no-transform"
    response["Connection"] = "keep-alive"
    response["X-Accel-Buffering"] = "no"
    return response
