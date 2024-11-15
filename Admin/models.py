from django.db import models
from nanoid import generate

# Create your models here.

class Brand(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ForeignKey('Common.Image', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate(size=40)
        super(Brand, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'brand'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'


class Banner(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    image = models.ForeignKey('Common.Image', on_delete=models.CASCADE)
    small_image = models.ForeignKey('Common.Image', on_delete=models.CASCADE, related_name='small_image', null=True, blank=True)
    button = models.JSONField()
    position = models.CharField(max_length=100, null=True, blank=True)
    priority = models.IntegerField()
    type  = models.CharField(max_length=100, choices=[('banner', 'Banner'), ('slider', 'Slider')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate(size=40)
        super(Banner, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'banner'
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'


class BannerGroup(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    banners = models.ManyToManyField(Banner)
    location = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate(size=40)
        super(BannerGroup, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'banner_group'
        verbose_name = 'Banner Group'
        verbose_name_plural = 'Banner Groups'


class Page(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    slug = models.CharField(max_length=200)
    title = models.CharField(max_length=500)
    description = models.TextField()
    image = models.ForeignKey('Common.Image', on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_last = models.BooleanField(default=True)
    content = models.JSONField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate(size=40)
        super(Page, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'page'
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        unique_together = ['slug', 'is_last']


class RBoxImage(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    image = models.ForeignKey('Common.Image', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate(size=40)
        super(RBoxImage, self).save(*args, **kwargs)

    def __str__(self):
        return self.id
    
    class Meta:
        db_table = 'rbox_image'
        verbose_name = 'RBox Image'
        verbose_name_plural = 'RBox Images' 


class RBox(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    images = models.ManyToManyField(RBoxImage)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate(size=40)
        super(RBox, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'rbox'
        verbose_name = 'RBox'
        verbose_name_plural = 'RBoxes'  