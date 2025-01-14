from django.db import models
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from PIL import Image
import boto3
from django.conf import settings
import io
import os
import sys

IS_DEVELOPMENT = 'dev' in sys.prefix.lower()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        default='profile_pics/default.png',
        upload_to='profile_pics/',
        blank=True,
        null=True
    )
    
    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        img = None
        buffer = None
        if self.profile_picture:
            try:
                # Open the image from the profile_picture field
                img = Image.open(self.profile_picture)

                # Convert the image to RGB
                img = img.convert('RGB')

                # Perform operations on the image
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG')
                buffer.seek(0)
                file_content = buffer.getvalue()
                file_name = f'{self.user.username}_profile.jpg'

                if IS_DEVELOPMENT:
                    # Save the resized image to the local storage
                    file_like_object = io.BytesIO(file_content)
                    default_storage.save(f'media/profile_pics/{file_name}', file_like_object )
                else:
                    # Save the resized image to s3
                    s3 = boto3.client('s3')
                    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                    s3.put_object(Bucket=bucket_name, Key=f'profile_pics/{file_name}', Body=file_content)

                # Update the profile picture field to point to the S3 URL
                self.profile_picture = f'profile_pics/{file_name}'

            except FileNotFoundError:
                # Handle the error (e.g., log it, set a default image, etc.)
                pass

            finally:
                if img:
                    img.close()
                if buffer:
                    buffer.close()

        super().save(*args, **kwargs)
