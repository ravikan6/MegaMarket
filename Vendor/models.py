from django.db import models
from nanoid import generate

# Create your models here.

class Vendor(models.Model):
    key = models.CharField(max_length=24, unique=True, editable=False)
    user = models.OneToOneField('User.User', on_delete=models.CASCADE)
    store_name = models.CharField(max_length=100)
    store_description = models.TextField(blank=True)
    store_logo = models.ForeignKey('Common.Image', on_delete=models.SET_NULL, null=True, blank=True, related_name='store_logo')
    store_banner = models.ForeignKey('Common.Image', on_delete=models.SET_NULL, null=True, blank=True, related_name='store_banner')
    store_address = models.TextField(blank=True)
    store_phone = models.CharField(max_length=15, blank=True)
    store_email = models.EmailField(blank=True, null=True)
    store_website = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.user.type.lower() != 'vendor':
            raise ValueError('User type must be vendor')
        if not self.pk:
            self.key = generate(size=24)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.store_name
    
    class Meta:
        db_table = 'vendor'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
