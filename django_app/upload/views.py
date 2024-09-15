from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect

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


def homepage(request):
    return render(request, 'tutorials_webpage.html')


def ai(request):
    return HttpResponseRedirect("http://192.168.0.104:8080")
