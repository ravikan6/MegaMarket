from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
import json
from Inventory.models import Order
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from User.Utils.tools import generate_otp
from User.models import EmailVerifications, User
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect

# Create your views here.

def cashfree_webhook(request: HttpRequest):
    if request.method == 'POST':
        payload = json.loads(request.body.decode('utf-8'))
        print(payload)
        order_id = payload['data']['order']['order_id']
        payment_status = payload['data']['payment']['payment_status']
        payment_amount = payload['data']['payment']['payment_amount']
        customer_id = payload['data']['customer_details']['customer_id']
        
        order = Order.objects.get(order_id=order_id)
        order.payment_status = payment_status
        order.status = 'confirmed' if payment_status == 'PAID' else 'pending'
        order.save()

        # Process the payload as needed
        print(f"Order ID: {order_id}")
        print(f"Payment Status: {payment_status}")
        print(f"Payment Amount: {payment_amount}")
        print(f"Customer ID: {customer_id}")
        
    return HttpResponse('Webhook received')

@csrf_exempt
def login(request):
    redirect_url = request.GET.get('next') or request.GET.get('callback_url') or request.GET.get('callback') or '/'
    if request.user.is_authenticated:
        return redirect(redirect_url)
    if request.method == 'GET':
        return render(request, 'auth/login.html')
    payload = request.POST
    email = payload.get('email')
    password = payload.get('password')
    user = authenticate(request, email=email, password=password)
    if user is not None:
        auth_login(request, user)
        return redirect(redirect_url)
    else:
        return render(request, 'auth/login.html', {'error': 'Invalid email or password'})
        

@csrf_exempt
def signup(request):
    redirect_url = request.GET.get('next') or request.GET.get('callback_url') or request.GET.get('callback') or '/'
    if request.user.is_authenticated:
        return redirect(redirect_url)
    if request.method == 'POST':
        try:
            payload = request.POST
            email = payload.get('email')
            password = payload.get('password')
            first_name = payload.get('first_name')
            last_name = payload.get('last_name')
            phone_number = payload.get('full_mobile')

            if User.objects.filter(email=email).exists():
                return render(request, 'auth/signup.html', {'message': 'Email already registered'})

            user = User.objects.create_user(email=email, first_name=first_name, last_name=last_name, phone_number=phone_number)
            user.set_password(password)
            user.save()
            auth_login(request, user)
            return redirect(redirect_url)
        except Exception as e:
            return render(request, 'auth/signup.html', {'message': str(e)})

    return render(request, 'auth/signup.html')


@csrf_exempt
@require_POST
def verify_email(request):
    payload = json.loads(request.body.decode('utf-8'))
    email = payload.get('email')
    otp = payload.get('otp')
    vfc = EmailVerifications.objects.filter(
        email=email, otp=otp, expires_at__gte=datetime.now()).first()
    if not vfc:
        return JsonResponse({'success': False, 'message': 'Invalid OTP'}, status=400)
    vfc.delete()
    return JsonResponse({'success': True, 'message': 'Email verified successfully'}, status=200)

@csrf_exempt
@require_POST
def send_verification(request):
    payload = json.loads(request.body.decode('utf-8'))
    email = payload.get('email')
    user = User.objects.filter(email=email, is_active=True).first()
    if user:
        return JsonResponse({'success': False, 'message': 'Email already registered'}, status=400)
    otp_code = generate_otp()
    vfc = EmailVerifications.objects.create(
        email=email, otp=otp_code, expires_at=timezone.now() + timedelta(minutes=10))
    sent = vfc.send_verification_email_otp()
    if not sent:
        return JsonResponse({'success': False, 'message': 'Failed to send verification email'}, status=500)
    return JsonResponse({'success': True, 'message': 'Verification email sent successfully'}, status=200)


def forget_password(request):
    if request.method == 'GET':
        return render(request, 'auth/forget_password.html')
    email = request.POST.get('email')
    user = User.objects.filter(email=email).first()
    if not user:
        return render(request, 'auth/forget_password.html', {'error': 'Email not registered'})
    otp_code = generate_otp()
    vfc = EmailVerifications.objects.create(
        email=email, otp=otp_code, expires_at=timezone.now() + timedelta(minutes=10))
    sent = vfc.send_verification_email_otp()
    if not sent:
        return render(request, 'auth/forget_password.html', {'error': 'Failed to send OTP'})
    return render(request, 'auth/forget_password.html', {'success': 'OTP sent successfully'})