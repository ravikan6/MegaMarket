from django.contrib import admin
from .models import Inventory, Item, Category, ItemReview, Order, OrderItem, Tag, ItemVariation
# Register your models here.

admin.site.register(Inventory)
admin.site.register(Item)
admin.site.register(Category)
admin.site.register(ItemReview)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Tag)
admin.site.register(ItemVariation)