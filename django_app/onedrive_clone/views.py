from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import File
from .forms import FileUploadForm

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.user = request.user
            file_instance.size = request.FILES['file'].size
            file_instance.save()
            return redirect('file_list')
    else:
        form = FileUploadForm()
    return render(request, 'onedrive_clone/upload.html', {'form': form})

@login_required
def file_list(request):
    files = File.objects.filter(user=request.user)
    for file in files:
        print(f"{file.filename}: is_image -> {file.is_image()}")
    return render(request, 'onedrive_clone/file_list.html', {'files': files})

@login_required
def download_file(request, file_id):
    file = File.objects.get(id=file_id, user=request.user)
    response = HttpResponse(file.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file.filename}"'
    return response
