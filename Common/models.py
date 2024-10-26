from django.db import models
from nanoid import generate

# Create your models here.

class Image(models.Model):
    id = models.CharField(max_length=40, unique=True, editable=False, primary_key=True)
    url = models.CharField(max_length=255)
    alt = models.CharField(max_length=255, blank=True, null=True)
    caption = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    provider = models.CharField(max_length=255, default='cloudinary')

    has_url = False
    _url = None
    
    class Meta:
        db_table = 'images'
        verbose_name = 'image'
        verbose_name_plural = 'images'

    def __str__(self):
        return self.url
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.id = generate(size=40)
        super().save(*args, **kwargs)
        return self
    
    def get_url(self):
        return self.url
    

class ItemMedia(models.Model):
    id = models.CharField(max_length=40, unique=True, editable=False, primary_key=True)
    url = models.CharField(max_length=255)
    alt = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=100) # image, video, audio
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    provider = models.CharField(max_length=255, default='cloudinary')

    has_url = False
    _url = None

    class Meta:
        db_table = 'item_media'
        verbose_name = 'item media'
        verbose_name_plural = 'item media'

    def __str__(self):
        return self.url
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.id = generate(size=40)
        super().save(*args, **kwargs)
        return self
    
    def get_url(self):
        return self.url