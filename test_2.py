import os
import django
import sys

# Add the base project folder to sys.path (not the subfolder)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'django_blog_project')))

# Set the DJANGO_SETTINGS_MODULE environment variable to the settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_blog_project.settings'

# Initialize Django
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO

# Create a mock file to simulate uploading an image
file_content = BytesIO(b"dummy data representing an image file")
file_name = 'test_image.jpg'
file = ContentFile(file_content.getvalue(), file_name)

# Using the default storage to save the file
file_path = default_storage.save(f'profile_pictures/{file_name}', file)

# Check where the file has been stored (S3 path)
print(f"File uploaded to: {file_path}")
