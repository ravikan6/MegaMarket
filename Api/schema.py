import graphene
import os
import requests
from User.schema import Query as UserQuery, Mutation as UserMutation
from Common.schema import Query as CommonQuery, Mutation as CommonMutation
from Inventory.schema import Query as InventoryQuery, Mutation as InventoryMutation
from Admin.schema import Query as AdminQuery, Mutation as AdminMutation
from Vendor.schema import Query as VendorQuery, Mutation as VendorMutation


class ValidateUPIResponse(graphene.ObjectType):
    success = graphene.Boolean()
    customer_name = graphene.String()
    vpa = graphene.String()
    res = graphene.String()

class ValidateUPIMutation(graphene.Mutation):
    class Arguments:
        upi = graphene.String(required=True)

    Output = ValidateUPIResponse

    def mutate(self, info, upi):
        if not info.context.user.is_authenticated:
            return None
        api_key = os.environ.get('RAZORPAY_API_KEY')
        api_secret = os.environ.get('RAZORPAY_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("RAZORPAY_API_KEY and RAZORPAY_API_SECRET must be set in environment variables")
        
        url = "https://api.razorpay.com/v1/payments/validate/vpa"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "vpa": upi
        }
        
        response = requests.post(url, auth=(api_key, api_secret), headers=headers, json=data)
        response_data = response.json()
        
        success = response_data.get('success', False)
        customer_name = response_data.get('customer_name', '')
        vpa = response_data.get('vpa', '')

        return ValidateUPIResponse(success=success, customer_name=customer_name, vpa=vpa, res=str(response_data))

class Query(UserQuery, CommonQuery, InventoryQuery, AdminQuery, VendorQuery):
    greet = graphene.String(name=graphene.String(default_value="stranger"))
    
    def resolve_greet(self, info, name = None):
        return f'Hello {name}!'

class Mutation(UserMutation, CommonMutation, InventoryMutation, AdminMutation, VendorMutation):
    validate_upi = ValidateUPIMutation.Field()
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)