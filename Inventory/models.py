from django.db import models
from nanoid import generate

# Create your models here.

class Inventory(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    variant = models.ForeignKey('ItemVariantValue', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
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
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=250, null=True, blank=True)
    teaser = models.CharField(max_length=500, null=True, blank=True)
    description = models.JSONField(null=True, blank=True)
    image = models.ForeignKey('Common.Image', on_delete=models.CASCADE, null=True, blank=True)
    media = models.ManyToManyField('Common.ItemMedia', related_name='media', through='ItemMediaThrough')
    seo = models.JSONField(null=True, blank=True)
    tags = models.ManyToManyField('Tag', related_name='item_tags')
    status = models.CharField(max_length=100, choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ], default='draft')

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax = models.BooleanField(default=True, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    can_return = models.BooleanField(default=True, null=True, blank=True)
    return_time = models.IntegerField(null=True, blank=True)
    
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey('Vendor.Vendor', on_delete=models.CASCADE)
    brand = models.ForeignKey('Admin.Brand', on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    
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

class ItemMediaThrough(models.Model):
    item = models.ForeignKey('Inventory.Item', on_delete=models.CASCADE)
    item_media = models.ForeignKey('Common.ItemMedia', on_delete=models.CASCADE)

    class Meta:
        db_table = 'inventory_item_media'

class ItemVariation(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='variations')
    name = models.CharField(max_length=100)
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
        unique_together = ['item', 'name']

class ItemVariantValue(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    variant = models.ForeignKey('ItemVariation', on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)
    media = models.ManyToManyField('Common.ItemMedia')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.id = generate(size=28)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.value
    
    class Meta:
        db_table = 'item_variant_value'
        verbose_name = 'Item Variant Value'
        verbose_name_plural = 'Item Variant Values'
        unique_together = ['item', 'variant', 'value']

class Category(models.Model):
    id = models.CharField(max_length=100, unique=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ForeignKey('Common.Image', on_delete=models.CASCADE, null=True, blank=True)
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