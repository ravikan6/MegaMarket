from django.urls import path, include

from Admin.views import cashfree_webhook


webhook = [
    path('cashfree/', cashfree_webhook, name='cashfree_webhook'),
]