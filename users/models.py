from django.db import models
from django.core.files.storage import default_storage
from django.contrib.auth.models import User


    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        default='profile_pics/default.png',
        blank=True,
        null=True
        )
    
    def save(self, *args, **kwargs):
        print(self.profile_picture.url)  # This will print the URL of the uploaded image.
        super(Profile, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
        
    #     img = Image.open(self.image.path)
        
    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)