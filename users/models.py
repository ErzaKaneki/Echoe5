from django.db import models
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
import boto3
from django.core.files.base import ContentFile
from django.conf import settings
import sys

IS_DEVELOPMENT = 'dev' in sys.prefix.lower()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        default='profile_pics/default.png',
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        img = None
        buffer = None 
        if self.profile_picture:
            try:
                # get the image from the profile_picture field
                img = Image.open(self.profile_picture)

                # convert the image to RGB
                img = img.convert('RGB')

                # resize image
                img = img.resize((150, 150), Image.Resampling.LANCZOS)

                # Save resized image to BytesIO object
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                buffer.seek(0)

                # Create a new ContentFile
                file_content = ContentFile(buffer.getvalue())
                file_name = f'{self.user.username}_profile.jpg'
                
                if IS_DEVELOPMENT:
                    # Save the resized image to the local storage
                    default_storage.save(f'media/profile_pics/{file_name}', file_content)
                else:
                    # Save the resized image to s3
                    s3 = boto3.client('s3')
                    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                    s3.put_object(Bucket=bucket_name, Key=f'profile_pics/{file_name}', Body=file_content)

                # Update the profile picture field to the point to S3 URL
                self.profile_picture = f'profile_pics/{file_name}'
                
            except FileNotFoundError:
                pass

            finally:
                if img:
                    img.close()
                if buffer:
                    buffer.close()

        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     print(self.profile_picture.url)  # This will print the URL of the uploaded image.
    #     super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} Profile'
