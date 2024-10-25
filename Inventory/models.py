from django.db import models
from nanoid import generate

# Create your models here.

class Inventory(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    variant = models.ForeignKey('ItemVariation', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    restock_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.id = generate(size=28)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'inventory'
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'
        unique_together = ['item', 'variant']

class Item(models.Model):
    key = models.CharField(max_length=100, unique=True, editable=False)
    sku = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=250)
    teaser = models.CharField(max_length=500, null=True, blank=True)
    description = models.JSONField(null=True, blank=True)
    image = models.ForeignKey('Common.Image', on_delete=models.CASCADE)
    images = models.ManyToManyField('Common.Image', related_name='item_images')
    tags = models.ManyToManyField('Tag', related_name='item_tags')
    status = models.CharField(max_length=100, choices=[
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('coming_soon', 'Coming Soon'),
        ('discontinued', 'Discontinued'),
    ], default='available')

    price = models.DecimalField(max_digits=10, decimal_places=2)
    cross_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=100, choices=[
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], null=True, blank=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    can_return = models.BooleanField(default=True, null=True, blank=True)
    return_time = models.IntegerField(null=True, blank=True)
    return_policy = models.JSONField(null=True, blank=True)
    
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    vendor = models.ForeignKey('Vendor.Vendor', on_delete=models.CASCADE)
    brand = models.ForeignKey('Admin.Brand', on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    extra_fields = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.key = generate(size=24)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'item'
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
    

class ItemVariation(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='variations')
    info = models.JSONField(null=True, blank=True)
    images = models.ManyToManyField('Common.Image', related_name='variation_images')
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.id = generate(size=28)
        super().save(*args, **kwargs)

    def __str__(self):

        return self.item.name
    
    class Meta:
        db_table = 'item_variation'
        verbose_name = 'Item Variation'
        verbose_name_plural = 'Item Variations'
        unique_together = ['item', 'info']

class Category(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ForeignKey('Common.Image', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    priority = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.id = generate(size=28)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    

class Tag(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.id = generate(size=28)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'tag'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class ItemReview(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    variant = models.ForeignKey('ItemVariation', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('User.User', on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.id = generate(size=28)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'item_review'
        verbose_name = 'Item Review'
        verbose_name_plural = 'Item Reviews'
        unique_together = ['item', 'user']
    

class Order(models.Model):
    key = models.CharField(max_length=100, unique=True, editable=False)
    user = models.ForeignKey('User.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10)  
    delivery_time = models.IntegerField( null=True, blank=True)
    shipping_address = models.ForeignKey('User.Address', on_delete=models.CASCADE, related_name='shipping_address')
    billing_address = models.ForeignKey('User.Address', on_delete=models.CASCADE, related_name='billing_address')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.key = generate(size=40)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Order by {self.user.get_full_name()} for {self.total} {self.currency}'
    
    class Meta:
        db_table = 'order'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    variant = models.ForeignKey('ItemVariation', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.quantity} x {self.item.name}'
    
    class Meta:
        db_table = 'order_item'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        unique_together = ['order', 'item', 'variant']