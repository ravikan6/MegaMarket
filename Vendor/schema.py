import graphene

from Api import relay
from Common.tools import ImageHandler
from User.models import User
from Vendor.types import NewVendorInput, UpdateVendorInput
from .models import Vendor
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

class VendorObject(DjangoObjectType):
    
    class Meta:
        model = Vendor
        fields = '__all__'
        filter_fields = {
            'key': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )
        use_connection = True


class NewVendor(graphene.Mutation):

    class Input:
        input = NewVendorInput(required=True)

    vendor = graphene.Field(VendorObject)
    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, input: NewVendorInput | None = None):
        user = User.objects.create_user(
            username=input.username,
            first_name=input.first_name,
            last_name=input.last_name,
            email=input.email,
            password=input.password,
            dob = input.dob,
            sex = input.sex
        )
        if input.image:
            user.image = ImageHandler(input.image).auto_image()
            user.save()
        vendor = Vendor(
            user=user,
            name=input.store.name,
            description=input.store.description,
            logo=ImageHandler(input.store.logo).auto_image(),
            banner=ImageHandler(input.store.banner).auto_image(),
            address=input.store.address,
            phone=input.store.phone,
            email=input.store.email,
            website=input.store.website
        )
        return NewVendor(vendor=vendor, success=True)
    

class UpdateVendor(graphene.Mutation):
    class Input:
        input = UpdateVendorInput(required=True)

    vendor = graphene.Field(VendorObject)
    message = graphene.String()
    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, input: UpdateVendorInput | None = None):
        user = info.context.user
        if not user.is_authenticated or not user.type == 'vendor':
            return UpdateVendor(message="Authentication credentials were not provided or user is not a vendor", success=False)
        vendor = user.vendor
        if input.store_name:
            vendor.name = input.store_name
        if input.store_description:
            vendor.description = input.store_description
        if input.store_logo:
            vendor.logo = ImageHandler(input.store_logo).auto_image()
        if input.store_banner:
            vendor.banner = ImageHandler(input.store_banner).auto_image()
        if input.store_address:
            vendor.address = input.store_address
        if input.store_phone:
            vendor.phone = input.store_phone
        if input.store_email:
            vendor.email = input.store_email
        if input.store_website:
            vendor.website = input.store_website
        vendor.save()
        return UpdateVendor(vendor=vendor, success=True)


class Query:
    vendor = relay.Node.Field(VendorObject)
    vendors = DjangoFilterConnectionField(VendorObject)
    

class Mutation:
    new_vendor = NewVendor.Field()
    update_vendor = UpdateVendor.Field()