from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import json
from Inventory.models import Order

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