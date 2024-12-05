from django.urls import path, include

from Admin.views import cashfree_webhook, login, signup, verify_email, send_verification, forget_password


webhook = [
    path('cashfree/', cashfree_webhook, name='cashfree_webhook'),
]

auth = [
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('verify-email/', verify_email, name='verify_email'),
    path('send-verification/', send_verification, name='send_verification'),
    path('forget-password/', forget_password, name='forget_password'),
]