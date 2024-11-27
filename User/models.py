from django.db import models

# Create your models here.
from django.core import validators
from django.utils.deconstruct import deconstructible

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from User.Utils.config import UserManager
from nanoid import generate

from User.Utils.tools import send_verification_email_otp


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r"^[a-zA-Z0-9_]{3,30}$"
    message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and _ characters."
    )
    flags = 0


class User(AbstractBaseUser, PermissionsMixin):
    key = models.CharField(max_length=24, unique=True, editable=False)
    username_validator = UsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=190,
        unique=True,
        help_text=_(
            'Required. 190 characters or fewer. Letters, digits and _ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },)
    email = models.EmailField(
        _('email address'),
        unique=True,
        max_length=254,
        help_text=_('Required. Enter a valid email address.'),
        error_messages={
            'unique': _("A user with that email already exists."),
        },)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    image = models.ForeignKey(
        'Common.Image', on_delete=models.SET_NULL, null=True, blank=True)
    sex = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    type = models.CharField(max_length=20, default='customer', choices=(
        ('user', 'User'),
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
    ))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'auth_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @property
    def is_vendor(self):
        return self.type.lower() == 'vendor'

    @property
    def is_admin(self):
        return self.is_superuser or self.type.lower() == 'admin'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.pk:
            self.key = generate(size=24)
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Address(models.Model):
    id = models.CharField(max_length=100, unique=True,
                          editable=False, primary_key=True)
    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=250)
    address_line_2 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    type = models.CharField(max_length=20, default='home', choices=(
        ('home', 'Home'),
        ('office', 'Office'),
        ('other', 'Other'),
    ))
    is_billing = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.id = generate(size=28)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    class Meta:
        db_table = 'address'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        unique_together = ['user', 'name']


class EmailVerifications(models.Model):
    id = models.CharField(max_length=100, unique=True,
                          editable=False, primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             related_name='email_verifications', null=True, blank=True)
    email = models.EmailField(max_length=254)
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.id = generate(size=28)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def send_verification_email_otp(self):
        return send_verification_email_otp(self.email, self.otp)

    class Meta:
        db_table = 'email_verification'
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'


class CartItem(models.Model):
    cart = models.ForeignKey(
        'Cart', on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey('Inventory.Item', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    variants = models.ManyToManyField(
        'Inventory.ItemVariantValue', related_name='cart_items')

    def __str__(self):
        return f"{self.quantity} of {self.item.name} in cart {self.cart.id}"

    class Meta:
        db_table = 'cart_item'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'


class Cart(models.Model):
    id = models.CharField(max_length=100, unique=True,
                          editable=False, primary_key=True)
    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.id = generate(size=28)
        super().save(*args, **kwargs)

    def total(self):
        total = 0
        for item in self.items.all():
            total += item.item.price * item.quantity
        return total

    def total_items(self):
        return self.items.count()

    def __str__(self):
        return f'Shopping Bag of {self.user.username if self.user else "Guest"}'

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'


class Wishlist(models.Model):
    id = models.CharField(max_length=100, unique=True,
                          editable=False, primary_key=True)
    user = models.OneToOneField(
        'User', on_delete=models.CASCADE, related_name='wishlist', auto_created=True)
    items = models.ManyToManyField(
        'Inventory.Item', related_name='wishlist_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.id = generate(size=28)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'wishlist'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'
