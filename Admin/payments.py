import razorpay
import datetime
import os
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
import jwt

from Inventory.models import Order
from User.models import User

Cashfree.XClientId = os.environ.get('CASHFREE_CLIENT_ID')
Cashfree.XClientSecret = os.environ.get('CASHFREE_CLIENT_SECRET')
Cashfree.XEnvironment = Cashfree.PRODUCTION if os.environ.get(
    'CASHFREE_ENVIRONMENT') == 'PRODUCTION' else Cashfree.SANDBOX
x_api_version = "2023-08-01"


class Payments:
    def __init__(self, method='other'):
        self.method = method
        self.cashfree = Cashfree()
        self.order_meta = OrderMeta()

    def create_order(self, customer: User, order: Order):
        if not customer or customer.is_anonymous or not customer.is_authenticated:
            raise Exception('You must be logged in to perform this action.')
        if not order:
            raise Exception('Invalid order.')
        return_url = os.environ.get('CASFREE_RETURN_URL')
        if not return_url:
            raise Exception('Return URL not found.')
        try:
            customer_details = CustomerDetails(
                customer_id=customer.key, customer_phone=customer.phone_number)
            customer_details.customer_name = customer.get_full_name()
            customer_details.customer_email = customer.email
            # customer_details.customer_uid = customer.key

            expire_time = datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(minutes=16)

            token = self.generate_token({
                'order_id': order.order_id,
                'user_id': customer.key,
                'amount': str(order.total),
                'exp': expire_time
            })

            print(token)

            self.order_meta.return_url = f'{return_url}?order_id={order.order_id}&token={token}'
            self.order_meta.notify_url = os.environ.get('CASHFREE_NOTIFY_URL')
            print(self.order_meta.notify_url)
            self.order_meta.payment_methods = "cc,dc,ccc,nb,upi"

            create_order_request = CreateOrderRequest(
                order_amount=float(order.total),
                order_currency=order.currency or 'INR',
                customer_details=customer_details
            )
            create_order_request.order_id = order.order_id
            create_order_request.order_meta = self.order_meta
            create_order_request.order_expiry_time = expire_time.isoformat()
            create_order_request.order_note = f'Order for {
                customer.get_full_name()} with order ID {order.order_id}'

            response = self.cashfree.PGCreateOrder(
                x_api_version, create_order_request)
            if response.status_code == 200:
                return response
            else:
                raise Exception(response.status_code, response.data)
        except Exception as e:
            print(e, 'Error creating order with Cashfree.')
            return None

    def generate_token(self, payload: dict):
        secret_key = os.environ.get('CASHFREE_CLIENT_SECRET')
        payload = {
            'orderId': payload['order_id'],
            'userId': payload['user_id'],
            'amount': payload['amount'],
            'exp': payload['exp']
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

    def verify_token(self, token: str):
        secret_key = os.environ.get('CASHFREE_CLIENT_SECRET')
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            return None

    def get_info(self, order_id):
        try:
            info = self.cashfree.PGFetchOrder(
                x_api_version=x_api_version, order_id=order_id)
            if info.status_code == 200:
                return info.data
            else:
                raise Exception("An error accured.")
        except:
            return None


client = razorpay.Client(auth=(os.environ.get('RAZORPAY_API_KEY'), os.environ.get('RAZORPAY_API_SECRET')))
client.set_app_details({"title": "MeraBestie - Django", "version": "1.0.0"})
