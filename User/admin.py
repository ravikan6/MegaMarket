from django.contrib import admin
from .models import User, Cart, CartItem, Wishlist, Address

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    pass

admin.site.register(User, UserAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(Address)