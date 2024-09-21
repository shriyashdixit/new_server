from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    filename = models.CharField(max_length=255)
    size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename

    def is_image(self):
        """Check if the uploaded file is an image by trying to open it with Pillow."""
        try:
            Image.open(self.file).verify()  # This verifies if the file is a valid image
            return True
        except (IOError, SyntaxError):
            return False

    def get_file_icon(self):
        """Return a suitable icon for non-image files."""
        extension = self.filename.split('.')[-1].lower()
        if extension in ['pdf']:
            return 'pdf_icon.png'  # Add icons to your static files
        elif extension in ['doc', 'docx']:
            return 'word_icon.png'
        elif extension in ['xls', 'xlsx']:
            return 'excel_icon.png'
        else:
            return 'file_icon.png'  # Default icon for unknown file types

class SharedFile(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    shared_with = models.EmailField()
    shared_at = models.DateTimeField(auto_now_add=True)

