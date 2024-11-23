from datetime import datetime, timedelta
from email import message
from graphene_django.filter import DjangoFilterConnectionField
import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth import authenticate, login
from nanoid import generate
from Api import relay
from Common.tools import ImageHandler
from Inventory.models import Item, ItemVariantValue
from User.Utils.tools import generate_otp
from User.types import BaseUpdateProfileInput, CustomerInput, SimpliFiedVariants, SimpliFiedVariantsValues
from .models import EmailVerifications, User, Cart, Address, CartItem, Wishlist

class UserObject(DjangoObjectType):
    name = graphene.String()
    email = graphene.String()

    class Meta:
        model = User
        exclude = ('password', 'is_superuser', 'is_staff')
        filter_fields = {
            'email': ['exact', 'icontains'],
            'username': ['exact', 'icontains']
        }
        interfaces = (relay.Node, )
        use_connection = True
    
    def resolve_name(self, info):
        return self.get_full_name()
    
    def resolve_email(self, info):
        user = info.context.user
        if user.is_anonymous or user.pk != self.pk:
            return self.email[0] + '*' * (self.email.index('@') - 1) + self.email[self.email.index('@'):]
        return self.email
    
class AddressObject(DjangoObjectType):
    class Meta:
        model = Address
        fields = '__all__'
        interfaces = (relay.Node, )
        use_connection = True


class CartItemObject(DjangoObjectType):
    variants_obj = graphene.List(SimpliFiedVariants)
    class Meta:
        model = CartItem
        fields = '__all__'
        interfaces = (relay.Node, )
        use_connection = True

    def resolve_variants_obj(self, info):
        # Get all variant values for this cart item
        variant_values = self.variants.all().select_related('variant')

        # Group by variant (variation)
        variants_map = {}
        for variant_value in variant_values:
            variation = variant_value.variant
            if variation.id not in variants_map:
                variants_map[variation.id] = {
                    'id': variation.id,
                    'name': variation.name,
                    'values': []
                }
            variants_map[variation.id]['values'].append({
                'id': variant_value.id,
                'value': variant_value.value
            })

        # Convert to list of SimpliFiedVariants objects
        return [
            SimpliFiedVariants(
                id=variant_data['id'],
                name=variant_data['name'],
                values=[
                    SimpliFiedVariantsValues(id=value['id'], value=value['value'])
                    for value in variant_data['values']
                ]
            )
            for variant_data in variants_map.values()
        ]

class CartObject(DjangoObjectType):

    class Meta:
        model = Cart
        fields = '__all__'
        interfaces = (relay.Node, )
        use_connection = True

    
class WishlistObject(DjangoObjectType):
    count = graphene.Int()

    class Meta:
        model = Wishlist
        fields = '__all__'
        interfaces = (relay.Node, )
        use_connection = True

    def resolve_count(self, info):
        return self.items.count()

class NewCustomer(graphene.Mutation):
    class Input:
        input = CustomerInput(required=True)

    user = graphene.Field(UserObject)
    message = graphene.String()
    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, input : CustomerInput | None =None):
        user = User.objects.get(email=input.email)
        if not user:
            return NewCustomer(user=None, success=False, message='Invalid email')
        if user.is_active:
            return NewCustomer(user=None, success=False, message='User already exists')
        _image = None
        if input.image:
            _image = ImageHandler(input.image).auto_image()
        user.set_password(input.password)
        user.first_name = input.first_name
        user.last_name = input.last_name
        user.username = input.username or user.username
        user.dob = input.dob or None
        user.sex = input.sex or None
        user.image = _image or user.image
        user.is_active = True
        user.save()
        return NewCustomer(user=user, success=True, message="Your account has been created")

class CreateNewCustomer(graphene.Mutation):
    class Input:
        email = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserObject)

    @classmethod
    def mutate(cls, root, info, email: str):
        user = User.objects.filter(email=email).first()
        if user and user.is_active:
            return CreateNewCustomer(success=False, message='A user with this email already exists')
        otp_code = generate_otp()
        vfc = EmailVerifications.objects.create(email=email, otp=otp_code, expires_at=datetime.now() + timedelta(minutes=10))
        sent = vfc.send_verification_email_otp()
        if not sent:
            return CreateNewCustomer(success=False, message='Failed to send verification email')
        if not user:
            _username = email[:2] + generate(alphabet="0123456789abcdefghijklmnopqrst",size=8) + email[2:2] + generate(alphabet="0123456789abcdefghijklmnopqrst",size=8)
            user = User.objects.create(email=email, username=_username, is_active=False)
        return CreateNewCustomer(success=True, user=user, message='Verification email sent')

class SendVerificationEmail(graphene.Mutation):
    class Input:
        email = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, email):
        otp_code = generate_otp()
        vfc = EmailVerifications.objects.create(email=email, otp=otp_code, expires_at=datetime.now() + timedelta(minutes=10))
        sent = vfc.send_verification_email_otp()
        if not sent:
            return SendVerificationEmail(success=False, message='Failed to send verification email')
        return SendVerificationEmail(success=True, message='Verification email sent')
    
class VerifyEmail(graphene.Mutation):
    class Input:
        email = graphene.String(required=True)
        otp = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, email, otp):
        vfc = EmailVerifications.objects.filter(email=email, otp=otp, expires_at__gte=datetime.now()).first()
        if not vfc:
            return VerifyEmail(success=False, message='Invalid OTP')
        vfc.delete()
        return VerifyEmail(success=True, message='Email verified')
    
class ForgotPassword(graphene.Mutation):
    class Input:
        email = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, email):
        user = User.objects.filter(email=email).first()
        if not user:
            return ForgotPassword(success=False, message='User not found')
        otp_code = generate_otp()
        vfc = EmailVerifications.objects.create(email=email, otp=otp_code, expires_at=datetime.now() + timedelta(minutes=10))
        sent = vfc.send_verification_email_otp()
        if not sent:
            return ForgotPassword(success=False, message='Failed to send verification email')
        return ForgotPassword(success=True, message='Verification email sent')
    

class ResetPassword(graphene.Mutation):
    class Input:
        email = graphene.String(required=True)
        otp = graphene.String(required=True)
        password = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, email, otp, password):
        vfc = EmailVerifications.objects.filter(email=email, otp=otp, expires_at__gte=datetime.now()).first()
        if not vfc:
            return ResetPassword(success=False, message='Invalid OTP')
        user = User.objects.filter(email=email).first()
        if not user:
            return ResetPassword(success=False, message='User not found')
        user.set_password(password)
        user.save()
        vfc.delete()
        return ResetPassword(success=True, message='Password reset successful')

class UserLogin(graphene.Mutation):
    class Input:
        identifier = graphene.String(required=True)
        password = graphene.String(required=True)
    
    user = graphene.Field(UserObject)
    session_id = graphene.String()
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, identifier, password):
        isEmail = '@' in identifier
        user = User.objects.filter(email=identifier).first() if isEmail else User.objects.filter(username=identifier).first()
        if not user or not user.is_active:
            return UserLogin(success=False, message='Invalid credentials')
        if not user.check_password(password):
            return UserLogin(success=False, message='Invalid credentials')
        user = authenticate(email=user.email, password=password)
        login(info.context, user)
        return UserLogin(user=user, success=True, session_id=info.context.session.session_key, message="You have been logged in")

class UpdateUserProfile(graphene.Mutation):

    class Input:
        input = BaseUpdateProfileInput(required=True)

    profile = graphene.Field(UserObject)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input: BaseUpdateProfileInput | None = None):
        user = info.context.user
        if not user.is_authenticated or not user.is_active:
            return UpdateUserProfile(success=False, message="User is not authenticated or not active")
        
        if input.first_name:
            user.first_name = input.first_name
        if input.last_name:
            user.last_name = input.last_name
        if input.username:
            user.username = input.username
        if input.dob:
            user.dob = input.dob
        if input.sex:
            user.sex = input.sex
        if input.image:
            user.image = ImageHandler(input.image).auto_image()
        
        user.save()
        return UpdateUserProfile(profile=user, success=True, message="Profile updated successfully")
    
class CartActionEnum(graphene.Enum):
    ADD = 'add'
    REMOVE = 'remove'
    INCREASE = 'increase'
    DECREASE = 'decrease'

class CartManageMutation(graphene.Mutation):
    class Arguments:
        item_key = graphene.String(required=True)
        action = graphene.Argument(CartActionEnum, required=True)
        quantity = graphene.Int(required=False, default_value=1)
        variants = graphene.List(graphene.String, required=False)
    
    success = graphene.Boolean()
    message = graphene.String()
    cart = graphene.Field(CartObject)

    @classmethod
    def mutate(cls, root, info, item_key, action: CartActionEnum, quantity=1, variants=None):
        user = info.context.user
        if user.is_anonymous:
            return cls(success=False, message="User is not authenticated")

        try:
            _variants = set()
            if variants:
                for variant in variants:
                    try:
                        v = ItemVariantValue.objects.get(pk=variant)
                        _variants.add(v)
                    except ItemVariantValue.DoesNotExist:
                        raise 'Product Variant not exists.'

            cart, created = Cart.objects.get_or_create(user=user)
            item = Item.objects.get(key=item_key, itemvariantvalue__in=_variants) if _variants else Item.objects.get(key=item_key)
            if not item:
                raise 'Product not exists'
            cart_item = CartItem.objects.filter(cart=cart, item=item, variants__in=_variants).distinct().first() if _variants else CartItem.objects.filter(cart=cart, item=item).first()

            if action.value in [CartActionEnum.ADD.value, CartActionEnum.INCREASE.value]:
                if quantity <= 0:
                    return cls(success=False, message="Quantity must be greater than 0")
                
                if cart_item:
                    cart_item.quantity += quantity
                    cart_item.save()
                else:
                    if action.value == CartActionEnum.INCREASE.value:
                        return cls(success=False, message="Item not found in cart")
                    cart_item = CartItem.objects.create(
                        cart=cart,
                        item=item,
                        quantity=quantity,
                    )
                    if _variants:
                        cart_item.variants.set(_variants)
                return cls(
                    success=True,
                    message=f"{'Added' if action.value == CartActionEnum.ADD.value else 'Increased'} {quantity} item(s)",
                    cart=cart
                )

            elif action.value == CartActionEnum.REMOVE.value:
                if not cart_item:
                    return cls(success=False, message="Item not found in cart")
                cart_item.delete()
                return cls(success=True, message="Item removed from cart", cart=cart)

            elif action.value == CartActionEnum.DECREASE.value:
                if not cart_item:
                    return cls(success=False, message="Item not found in cart")
                
                if cart_item.quantity <= quantity:
                    cart_item.delete()
                    return cls(success=True, message="Item removed from cart", cart=cart)
                
                cart_item.quantity -= quantity
                cart_item.save()
                return cls(
                    success=True,
                    message=f"Decreased quantity by {quantity}",
                    cart=cart
                )

        except Cart.DoesNotExist:
            return cls(success=False, message="Cart not found")
        except Exception as e:
            return cls(success=False, message=str(e))


class AddToWishlist(graphene.Mutation):
    class Input:
        item_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    wishlist = graphene.Field(WishlistObject)

    @classmethod
    def mutate(cls, root, info, item_id):
        user = info.context.user
        if user.is_anonymous:
            return AddToWishlist(success=False, message="User is not authenticated")
        wishlist = user.wishlist
        if not wishlist:
            wishlist = Wishlist.objects.create(user=user)
        item = wishlist.items.filter(id=item_id).first()
        if not item:
            wishlist.items.add(item_id)
        return AddToWishlist(success=True, message="Item added to wishlist", wishlist=wishlist)
    
class RemoveFromWishlist(graphene.Mutation):
    class Input:
        item_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    wishlist = graphene.Field(WishlistObject)

    @classmethod
    def mutate(cls, root, info, item_id):
        user = info.context.user
        if user.is_anonymous:
            return RemoveFromWishlist(success=False, message="User is not authenticated")
        wishlist = user.wishlist
        if not wishlist:
            return RemoveFromWishlist(success=False, message="Wishlist is empty")
        item = wishlist.items.filter(id=item_id).first()
        if not item:
            return RemoveFromWishlist(success=False, message="Item not found in wishlist")
        wishlist.items.remove(item_id)
        return RemoveFromWishlist(success=True, message="Item removed from wishlist", wishlist=wishlist)


class AddressTypeInputEnum(graphene.InputObjectType):
    HOME = 'Home'
    OFFICE = 'Office'
    OTHER = 'Other'

class AddressInput(graphene.InputObjectType):
    line1 = graphene.String(required=True)
    line2 = graphene.String()
    city = graphene.String(required=True)
    state = graphene.String(required=True)
    country = graphene.String(required=True)
    postal_code = graphene.String(required=True)
    phone = graphene.String(required=True)
    name = graphene.String(required=True)
    is_default = graphene.Boolean()
    type = graphene.Argument(AddressTypeInputEnum)
    is_billing = graphene.Boolean()

class AddressMutation(graphene.Mutation):
    class Arguments:
        input = AddressInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    address = graphene.Field(AddressObject)

    @classmethod
    def mutate(cls, root, info, input: AddressInput):
        user = info.context.user
        if user.is_anonymous:
            return cls(success=False, message="User is not authenticated")
        address = Address(user=user)
        address.address_line_1 = input.line1
        address.address_line_2 = input.line2
        address.city = input.city
        address.state = input.state
        address.country = input.country
        address.zip_code = input.postal_code
        address.phone = input.phone
        address.is_default = input.is_default
        address.name = input.name
        address.type = input.type.value or 'home'
        address.is_billing = input.is_billing or False
        address.save()
        return cls(success=True, message="Address added", address=address)
    
class UpdateAddressMutation(graphene.Mutation):
    class Arguments:
        input = AddressInput(required=True)
        address_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    address = graphene.Field(AddressObject)

    @classmethod
    def mutate(cls, root, info, input: AddressInput, address_id):
        user = info.context.user
        if user.is_anonymous:
            return cls(success=False, message="User is not authenticated")
        address = Address.objects.filter(user=user, id=address_id).first()
        if not address:
            return cls(success=False, message="Address not found")
        address.address_line_1 = input.line1 or address.address_line_1
        address.address_line_2 = input.line2 or address.address_line_2
        address.city = input.city or address.city
        address.state = input.state or address.state
        address.country = input.country or address.country
        address.zip_code = input.postal_code or address.zip_code
        address.phone = input.phone or address.phone
        address.name = input.name or address.name
        address.type = input.type.value or address.type
        address.is_billing = input.is_billing or address.is_billing
        address.save()
        return cls(success=True, message="Address updated", address=address)


class Query(graphene.ObjectType):
    users = DjangoFilterConnectionField(UserObject)
    me = graphene.Field(UserObject)
    cart = graphene.Field(CartObject)
    wishlist = graphene.Field(WishlistObject)
    
    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user
    
    def resolve_cart(self, info):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user.cart
    
    def resolve_wishlist(self, info):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user.wishlist

class Mutation(graphene.ObjectType):
    new_customer = NewCustomer.Field()
    create_new_customer = CreateNewCustomer.Field()
    update_profile = UpdateUserProfile.Field()
    send_verification_email = SendVerificationEmail.Field()
    verify_email = VerifyEmail.Field()
    user_login = UserLogin.Field()
    forgot_password = ForgotPassword.Field()
    reset_password = ResetPassword.Field()
    add_address = AddressMutation.Field()
    update_address = UpdateAddressMutation.Field()

    manage_cart = CartManageMutation.Field() 
    add_to_wishlist = AddToWishlist.Field()
    remove_from_wishlist = RemoveFromWishlist.Field()