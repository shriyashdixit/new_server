from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
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


