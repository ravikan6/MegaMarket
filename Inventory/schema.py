from decimal import Decimal
from time import timezone
import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from Admin.models import Brand
from Admin.payments import Payments, RazorpayPayments
from Api import relay
from Common.exceptions import InvalidImageException, InvalidModelIdException, UnAuthorizedException
from Common.models import Image, ItemMedia
from Common.tools import ImageHandler, MediaHandler
from Common.types import ImageInput, MediaInput
from Inventory.models import Item, Category, Order, OrderItem, Inventory, ItemVariation, ItemReview, Tag, ItemVariantValue, PipelineItem, CheckoutPipeline, PromoCode
from Inventory.types import CategoryInput, CategoryUpdateInput, CheckoutPipelineInput, CheckoutPipelineUpdateInput, CreateOrderInput, CreateOrderRes, ItemExtraFieldObject, ItemSeoObject, ItemVariantInfoObject, MakeOrderInput, NewItemInput, PaymentDetailsObject, RazoryPayPaymentInput, ShippingInfoObject, TextJsonFieldData, TextJsonFieldObject, UpdateItemInput, VerifyOrderInput
from User.types import SimpliFiedVariants, SimpliFiedVariantsValues
from Vendor.models import Vendor


class ItemObject(DjangoObjectType):
    description = graphene.String()
    info = graphene.List(TextJsonFieldObject)
    extra_fields = graphene.List(ItemExtraFieldObject)
    seo = graphene.Field(ItemSeoObject)
    shipping = graphene.Field(ShippingInfoObject)

    desc_json = graphene.JSONString()
    seo_json = graphene.JSONString()
    extra_fields_json = graphene.JSONString()

    variants_obj = graphene.List(SimpliFiedVariants)

    in_cart = graphene.Boolean()
    in_wishlist = graphene.Boolean()

    class Meta:
        model = Item
        exclude = ('created_at', 'updated_at')
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'slug': ['exact'],
            'category': ['exact'],
            'tags': ['exact'],
            'price': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'status': ['exact'],
            'vendor': ['exact'],
            'vendor__key': ['exact'],
            'brand': ['exact'],
            'key': ['exact'],
            'sku': ['exact'],
        }
        interfaces = (relay.Node, )
        use_connection = True

    def resolve_description(self, info):
        try:
            if self.description.get('desc', None):
                return self.description.get('desc')
            return None
        except:
            return None

    def resolve_info(self, info):
        try:
            if self.description.get('info', None):
                return self.description.get('info', None)
            return None
        except:
            return None

    def resolve_extra_fields(self, info):
        try:
            if self.extra_fields:
                return self.extra_fields
            return None
        except:
            return None

    def resolve_seo(self, info):
        try:
            if self.seo:
                return self.seo
            return None
        except:
            return None

    def resolve_extra_fields_json(self, info):
        return self.extra_fields

    def resolve_desc_json(self, info):
        return self.description

    def resolve_seo_json(self, info):
        return self.seo

    def resolve_variants_obj(self, info):
        # Get all variations for this item with their values
        variations = self.variations.all().prefetch_related('values')

        # Format into SimplifiedVariants objects
        variants = []
        for variation in variations:
            variant_values = [
                SimpliFiedVariantsValues(
                    id=value.id,
                    value=value.value
                ) for value in variation.values.all()
            ]

            variants.append(
                SimpliFiedVariants(
                    id=variation.id,
                    name=variation.name,
                    values=variant_values
                )
            )

        return variants

    def resolve_in_cart(self, info):
        user = info.context.user
        if user.is_authenticated:
            try:
                c = user.cart.items.filter(item=self).first()
                return True if c else False
            except:
                return False
        else:
            return False

    def resolve_in_wishlist(self, info):
        user = info.context.user
        if user.is_authenticated:
            try:
                w = user.wishlist.items.filter(pk=self.pk).first()
                return True if w else False
            except:
                return False
        else:
            return False


class CategoryObject(DjangoObjectType):
    class Meta:
        model = Category
        exclude = ('created_at', 'updated_at')
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'parent': ['exact'],
            'priority': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'id': ['exact'],
        }
        interfaces = (relay.Node, )
        use_connection = True


class OrderObject(DjangoObjectType):
    payment = graphene.Field(PaymentDetailsObject)

    class Meta:
        model = Order
        fields = '__all__'
        filter_fields = {
            'order_id': ['exact'],
            'user': ['exact'],
            'status': ['exact'],
            'created_at': ['exact', 'gt', 'gte', 'lt', 'lte'],
        }
        interfaces = (relay.Node, )
        use_connection = True

    def resolve_payment(self, info):
        try:
            p = RazorpayPayments().get_info(order_id=self.extra.get('order_id', None))
            return p
        except:
            return None
    
    @classmethod
    def get_queryset(cls, queryset, info):
        user = info.context.user
        if not user.is_authenticated:
            return queryset.none()
        if user.type == 'vendor':
            return queryset.filter(items__item__vendor=user.vendor).distinct()
        if user.type == 'customer':
            return queryset.filter(user=user)
        return queryset
    

class OrderItemObject(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = '__all__'
        filter_fields = {
            'order': ['exact'],
            'item': ['exact'],
            'quantity': ['exact', 'gt', 'gte', 'lt', 'lte'],
        }
        interfaces = (relay.Node, )
        use_connection = True


class InventoryObject(DjangoObjectType):
    class Meta:
        model = Inventory
        fields = '__all__'
        filter_fields = {
            'item': ['exact'],
            'quantity': ['exact', 'gt', 'gte', 'lt', 'lte'],
        }
        interfaces = (relay.Node, )
        use_connection = True


class ItemVariationObject(DjangoObjectType):
    class Meta:
        model = ItemVariation
        fields = '__all__'
        # interfaces= (relay.Node, )
        # use_connection = True


class ItemVariantValueObject(DjangoObjectType):
    in_cart = graphene.Boolean()

    class Meta:
        model = ItemVariantValue
        fields = '__all__'
        # filter_fields = {
        #     'variant': ['exact'],
        #     'value': ['exact', 'icontains', 'istartswith'],
        # }
        # interfaces= (relay.Node, )
        # use_connection = True

    def resolve_in_cart(self, info):
        user = info.context.user
        if user.is_authenticated:
            try:
                c = user.cart.items.filter(
                    item=self.item, variants__in=[self]).first()
                return True if c else False
            except:
                return False
        else:
            return False


class ItemReviewObject(DjangoObjectType):

    class Meta:
        model = ItemReview
        fields = '__all__'
        filter_fields = {
            'item': ['exact'],
            'user': ['exact'],
            'rating': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'review': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (relay.Node, )
        use_connection = True


class TagObject(DjangoObjectType):
    class Meta:
        model = Tag
        fields = '__all__'
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (relay.Node, )
        use_connection = True


class CheckoutPipelineObject(DjangoObjectType):
    class Meta:
        model = CheckoutPipeline
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'id': ['exact']
        }
        interfaces = (relay.Node, )
        use_connection = True


class CheckoutPipelineItemObject(DjangoObjectType):
    variants_obj = graphene.List(SimpliFiedVariants)

    class Meta:
        model = PipelineItem
        fields = '__all__'

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
                    SimpliFiedVariantsValues(
                        id=value['id'], value=value['value'])
                    for value in variant_data['values']
                ]
            )
            for variant_data in variants_map.values()
        ]


class PromoCodeObject(DjangoObjectType):
    class Meta:
        model = PromoCode
        fields = '__all__'
        filter_fields = {
            'code': ['exact', 'icontains', 'istartswith'],
            'discount': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'valid_from': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'valid_till': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'is_active': ['exact'],
        }
        interfaces = (relay.Node, )
        use_connection = True


'''********** Mutations **********'''


class CreateItem(graphene.Mutation):

    item = graphene.Field(ItemObject)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info):
        user = info.context.user
        if not user.is_authenticated or not user.is_vendor:
            raise UnAuthorizedException()

        try:
            vendor = user.vendor
            if not vendor:
                raise InvalidModelIdException(model="Vendor")

            item = Item(
                vendor=vendor,
            )
            item.save()
            return CreateItem(item=item, success=True, message="Item created successfully")
        except:
            return CreateItem(item=None, success=False, message="An error occurred while creating item")


class ItemImageUpdate(graphene.Mutation):
    class Input:
        key = graphene.String(required=True)
        image = ImageInput(required=True)

    item = graphene.Field(ItemObject)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, key, image):
        user = info.context.user
        if not user.is_authenticated or not user.is_vendor:
            raise UnAuthorizedException()

        try:
            item = Item.objects.get(key=key, vendor=user.vendor)
        except Item.DoesNotExist:
            raise InvalidModelIdException(model="Item")

        try:
            image = ImageHandler(image).auto_image()
            if not image or not isinstance(image, Image):
                raise InvalidImageException()
            item.image = image
            item.save()
            return ItemImageUpdate(item=item, success=True, message="Image updated successfully")
        except:
            return ItemImageUpdate(item=None, success=False, message="An error occurred while updating image")


class ItemMediaUpdate(graphene.Mutation):
    class Input:
        key = graphene.String(required=True)
        media = graphene.List(MediaInput, required=True)

    item = graphene.Field(ItemObject)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, key, media):
        user = info.context.user
        if not user.is_authenticated or not user.is_vendor:
            raise UnAuthorizedException()

        try:
            item = Item.objects.get(key=key, vendor=user.vendor)
        except Item.DoesNotExist:
            raise InvalidModelIdException(model="Item")

        try:
            for _media in media:
                media = MediaHandler(_media).auto_media()
                if not media or not isinstance(media, ItemMedia):
                    raise InvalidImageException()
                item.media.add(media)
            item.save()
            return ItemMediaUpdate(item=item, success=True, message="Media updated successfully")
        except:
            return ItemMediaUpdate(item=None, success=False, message="An error occurred while updating media")


class UpdateItem(graphene.Mutation):

    class Input:
        key = graphene.String(required=True)
        input = UpdateItemInput()

    item = graphene.Field(ItemObject)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, key, input: UpdateItemInput | None):
        user = info.context.user
        if not user.is_authenticated or not user.is_vendor:
            raise UnAuthorizedException()

        try:
            item = Item.objects.get(key=key, vendor=user.vendor)
        except Item.DoesNotExist:
            raise InvalidModelIdException(model="Item")
        try:
            if input.sku:
                item.sku = input.sku
            if input.name:
                item.name = input.name
            if input.teaser:
                item.teaser = input.teaser
            if input.slug:
                item.slug = input.slug
            _desc = {
                "desc": input.description if input.description else item.description.get('desc', None),
                # "info": input.description.info if input.description.info else item.description.get('info', None)
            }
            item.description = _desc
            if input.category:
                try:
                    item.category = Category.objects.get(id=input.category)
                except Category.DoesNotExist:
                    raise InvalidModelIdException(model="Category")
            if input.brand:
                try:
                    item.brand = Brand.objects.get(id=input.brand)
                except Brand.DoesNotExist:
                    raise InvalidModelIdException(model="Brand")
            if input.status:
                item.status = input.status.value
            if type(input.can_return) == bool:
                item.can_return = input.can_return
            if type(input.tax) == bool:
                item.tax = input.tax
            if input.cost:
                item.cost = Decimal(input.cost)
            if input.compare_price:
                item.compare_price = Decimal(input.compare_price)
            if input.price:
                item.price = Decimal(input.price)
            if input.return_time:
                item.return_time = input.return_time
            if input.extra_fields:
                item.extra_fields = input.extra_fields
            if input.seo:
                _seo = {
                    "title": input.seo.title if input.seo.title else item.seo.get('title', None),
                    "description": input.seo.description if input.seo.description else item.seo.get('description', None),
                    "slug": input.seo.slug if input.seo.slug else item.seo.get('slug', None),
                    "keywords": input.seo.keywords if input.seo.keywords else item.seo.get('keywords', None)
                }
                item.seo = _seo
            if input.shipping:
                _shipping = {
                    "is_physical": input.shipping.is_physical if input.shipping.is_physical else item.shipping.get('is_physical', None),
                    "weight": input.shipping.weight if input.shipping.weight else item.shipping.get('weight', None),
                    "unit": input.shipping.unit if input.shipping.unit else item.shipping.get('unit', None)
                }
                item.shipping = _shipping
            if input.tags:
                for tag in input.tags:
                    tag, new = Tag.objects.get_or_create(name=tag)
                    item.tags.add(tag)
            item.save()
            return UpdateItem(item=item, success=True, message="Item updated successfully")
        except Exception as e:
            return UpdateItem(item=None, success=False, message="An error occurred while updating item")


class DeleteItem(graphene.Mutation):
    class Input:
        key = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, key):
        user = info.context.user
        if not user.is_authenticated or not user.is_vendor:
            raise UnAuthorizedException()

        try:
            item = Item.objects.get(key=key)
        except Item.DoesNotExist:
            raise InvalidModelIdException(model="Item")

        item.delete()
        return DeleteItem(success=True, message="Item deleted successfully")


class CreateCategory(graphene.Mutation):
    class Arguments:
        input = CategoryInput(required=True)

    category = graphene.Field(CategoryObject)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, input: CategoryInput):
        user = info.context.user
        if not user.is_authenticated or not user.is_admin:
            raise UnAuthorizedException()

        _parent = None
        if input.parent:
            try:
                _parent = Category.objects.get(id=input.parent)
            except Item.DoesNotExist:
                raise InvalidModelIdException(model="Parent Category")
        try:
            _image = None
            if (input.image):
                _image = ImageHandler(input.image).auto_image()
                if not _image or not isinstance(_image, Image):
                    raise InvalidImageException()

            category = Category(
                name=input.name,
                description=input.description,
                image=_image,
                parent=_parent,
                priority=input.priority
            )
            category.save()
            return CreateCategory(category=category, success=True, message="Category created successfully")
        except:
            return CreateCategory(category=None, success=False, message="An error occurred while creating category")


class UpdateCategory(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = CategoryUpdateInput(required=True)

    category = graphene.Field(CategoryObject)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, input):
        user = info.context.user
        if not user.is_authenticated or not user.is_admin:
            raise UnAuthorizedException()

        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            raise InvalidModelIdException(model="Category")

        try:
            if input.name:
                category.name = input.name
            if input.description:
                category.description = input.description
            if input.image:
                image = ImageHandler(input.image).auto_image()
                if image:
                    if not isinstance(image, Image):
                        raise InvalidImageException()
                category.image = image
            if input.parent:
                try:
                    category.parent = Category.objects.get(id=input.parent)
                except Category.DoesNotExist:
                    raise InvalidModelIdException(model="Parent Category")
            if input.priority:
                category.priority = input.priority
            category.save()
            return UpdateCategory(category=category, success=True, message="Category updated successfully")
        except:
            return UpdateCategory(category=None, success=False, message="An error occurred while updating category")


class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated or not user.is_admin:
            raise UnAuthorizedException()

        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            raise InvalidModelIdException(model="Category")

        category.delete()
        return DeleteCategory(success=True, message="Category deleted successfully")


class CreateTag(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    tag = graphene.Field(TagObject)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, name):
        user = info.context.user
        if not user.is_authenticated or not user.is_admin:
            raise UnAuthorizedException()

        try:
            tag, new = Tag.objects.get_or_create(name=name)
            return CreateTag(tag=tag, success=True, message="Tag created successfully")
        except:
            return CreateTag(tag=None, success=False, message="An error occurred while creating tag")


class UpdateTag(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String(required=True)

    tag = graphene.Field(TagObject)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, name):
        user = info.context.user
        if not user.is_authenticated or not user.is_admin:
            raise UnAuthorizedException()

        try:
            tag = Tag.objects.get(id=id)
        except Tag.DoesNotExist:
            raise InvalidModelIdException(model="Tag")

        try:
            tag.name = name
            tag.save()
            return UpdateTag(tag=tag, success=True, message="Tag updated successfully")
        except:
            return UpdateTag(tag=None, success=False, message="An error occurred while updating tag")


class DeleteTag(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated or not user.is_admin:
            raise UnAuthorizedException()

        try:
            tag = Tag.objects.get(id=id)
        except Tag.DoesNotExist:
            raise InvalidModelIdException(model="Tag")

        tag.delete()
        return DeleteTag(success=True, message="Tag deleted successfully")


class CreateItemReview(graphene.Mutation):
    class Arguments:
        item = graphene.String(required=True)
        rating = graphene.Int(required=True)
        review = graphene.String(required=True)
        variant = graphene.String()

    review = graphene.Field(ItemReviewObject)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, item, rating, review, variant=None):
        user = info.context.user
        if not user.is_authenticated:
            raise UnAuthorizedException()

        try:
            item = Item.objects.get(key=item)
        except Item.DoesNotExist:
            raise InvalidModelIdException(model="Item")

        _variant = None
        if variant:
            try:
                _variant = ItemVariation.objects.get(id=variant)
            except ItemVariation.DoesNotExist:
                raise InvalidModelIdException(model="Item Variation")

        try:
            review = ItemReview(
                item=item,
                user=user,
                rating=rating,
                review=review,
                variant=_variant
            )
            review.save()
            return CreateItemReview(review=review, success=True, message="Review created successfully")
        except:
            return CreateItemReview(review=None, success=False, message="An error occurred while creating review")


class UpdateItemReview(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        rating = graphene.Int()
        review = graphene.String()

    review = graphene.Field(ItemReviewObject)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, rating=None, review=None):
        user = info.context.user
        if not user.is_authenticated:
            raise UnAuthorizedException()

        try:
            review = ItemReview.objects.get(id=id)
        except ItemReview.DoesNotExist:
            raise InvalidModelIdException(model="Item Review")

        try:
            if rating:
                review.rating = rating
            if review:
                review.review = review
            review.updated_at = timezone.now()
            review.save()
            return UpdateItemReview(review=review, success=True, message="Review updated successfully")
        except:
            return UpdateItemReview(review=None, success=False, message="An error occurred while updating review")


class DeleteItemReview(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise UnAuthorizedException()

        try:
            review = ItemReview.objects.get(id=id)
        except ItemReview.DoesNotExist:
            raise InvalidModelIdException(model="Item Review")

        review.delete()
        return DeleteItemReview(success=True, message="Review deleted successfully")


class CreateOrder(graphene.Mutation):

    class Input:
        input = CreateOrderInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    order = graphene.Field(CreateOrderRes)

    @classmethod
    def mutate(cls, root, info, input: CreateOrderInput):
        user = info.context.user
        if not user.is_authenticated or not user.is_active:
            raise UnAuthorizedException()
        try:
            shipping_address = user.addresses.get(id=input.shipping_address)
            billing_address = user.addresses.get(id=input.billing_address)
            if not shipping_address or not billing_address:
                raise Exception('Invalid shipping or billing address')
        except:
            return CreateOrder(order=None, success=False, message="Invalid shipping or billing address")

        try:
            order = Order(
                user=user,
                total=Decimal(input.total),
                payment_method=input.payment_method or 'other',
                shipping_address=shipping_address,
                billing_address=billing_address,
            )
            order.save()
        except Exception as e:
            return CreateOrder(order=None, success=False, message="An error occurred while creating order")

        try:
            for item in input.items:
                try:
                    _item = Item.objects.get(key=item.item)
                except Item.DoesNotExist:
                    order.delete()
                    return CreateOrder(order=None, success=False, message="Invalid item")
                order_item = OrderItem(
                    order=order,
                    item=_item,
                    quantity=item.quantity,
                    price=Decimal(item.price),
                    total=Decimal(item.total),
                )
                order_item.save()
                if item.variants and len(item.variants) > 0:
                    for variant in item.variants:
                        try:
                            _variant = ItemVariation.objects.get(id=variant)
                        except ItemVariation.DoesNotExist:
                            order.delete()
                            return CreateOrder(order=None, success=False, message="Invalid item variant")
                        order_item.variants.add(_variant)
        except Exception as e:
            order.delete()
            return CreateOrder(order=None, success=False, message="An error occurred while creating order items")

        try:
            if order and order.order_id:
                payment = Payments().create_order(user, order)
                if payment and payment.status_code == 200:
                    order.extra = payment.raw_data
                    order.save()
                    res = CreateOrderRes()
                    res.payment_session_id = payment.data.payment_session_id
                    res.order_id = order.order_id
                    res.amount = float(order.total)
                    res.status = order.status
                    res.method = order.payment_method
                    res.expiry_time = str(payment.data.order_expiry_time)

                    return CreateOrder(
                        success=True,
                        message="Order created successfully",
                        order=res
                    )
                else:
                    raise Exception('Error creating order with Cashfree.')
        except Exception as e:
            order.delete()
            return CreateOrder(order=None, success=False, message="An error occurred while creating order")


class VerifyGetOrder(graphene.Mutation):

    class Input:
        input = VerifyOrderInput(required=True)

    success = graphene.Boolean()
    order = graphene.Field(OrderObject)
    payment = graphene.Field(PaymentDetailsObject)

    def mutate(self, info, input: VerifyOrderInput):
        try:
            order = Order.objects.get(order_id=input.order_id)
        except:
            return VerifyGetOrder(success=False)
        isValid = Payments().verify_token(token=input.token)
        if not isValid:
            return VerifyGetOrder(success=False)
        payment = Payments().get_info(order_id=input.order_id)
        if not payment:
            return VerifyGetOrder(success=False)
        if payment.order_status == 'PAID':
            order.payment_status = 'paid'
        elif payment.order_status == 'ACTIVE':
            order.payment_status = 'pending'
        elif payment.order_status == 'EXPIRED':
            order.payment_status = 'failed'
        elif payment.order_status == 'TERMINATED':
            order.payment_status = 'failed'
        order.save()
        return VerifyGetOrder(success=True, order=order, payment=payment)


class CreateCheckoutPipeline(graphene.Mutation):
    class Arguments:
        input = CheckoutPipelineInput(required=True)

    pipeline = graphene.Field(CheckoutPipelineObject)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input: CheckoutPipelineInput):
        user = info.context.user
        if not user.is_authenticated:
            raise UnAuthorizedException()

        try:
            items = []
            for item in input.items:
                try:
                    _item = Item.objects.get(key=item.item)
                    _item_variants = []
                    for variant in item.variants:
                        _variant = ItemVariantValue.objects.get(id=variant)
                        _item_variants.append(_variant)
                    items.append({
                        'item': _item,
                        'quantity': item.quantity or 1,
                        'discount': item.discount or 0,
                        'variants': _item_variants
                    })
                except (Item.DoesNotExist, ItemVariantValue.DoesNotExist):
                    return cls(pipeline=None, success=False, message="Invalid item or variant")

            _pipeline_items = []
            for item in items:
                pipeline_item = PipelineItem.objects.create(
                    item=item['item'],
                    quantity=item['quantity'],
                    discount=item['discount']
                )
                pipeline_item.variants.set(item['variants'])
                _pipeline_items.append(pipeline_item)

            pipeline = CheckoutPipeline.objects.create(user=user)
            pipeline.items.set(_pipeline_items)
            pipeline.save()
            return cls(pipeline=pipeline, success=True, message="Pipeline created successfully")
        except Exception as e:
            return cls(pipeline=None, success=False, message=f"An error occurred while creating pipeline: {str(e)}")


class UpdateCheckoutPipeline(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = CheckoutPipelineUpdateInput(required=True)

    pipeline = graphene.Field(CheckoutPipelineObject)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, id, input: CheckoutPipelineUpdateInput):
        user = info.context.user
        if not user.is_authenticated:
            raise UnAuthorizedException()

        try:
            pipeline = CheckoutPipeline.objects.get(id=id, user=user)
        except CheckoutPipeline.DoesNotExist:
            raise InvalidModelIdException(model="Checkout Pipeline")

        try:
            if input.items:
                for item in input.items:
                    try:
                        if item.action == 'add':
                            _item = Item.objects.get(key=item.item)
                            _item_variants = []
                            for variant in item.variants:
                                _variant = ItemVariantValue.objects.get(
                                    id=variant)
                                _item_variants.append(_variant)
                            pipeline_item = PipelineItem.objects.create(
                                item=_item,
                                quantity=item.quantity or 1,
                                discount=item.discount or 0
                            )
                            pipeline_item.variants.set(_item_variants)
                            pipeline.items.add(pipeline_item)
                        elif item.action == 'remove' or item.action == 'update':
                            _item = Item.objects.get(key=item.item)
                            pipeline_item = pipeline.items.get(item=_item)
                            if item.action == 'remove':
                                pipeline.items.remove(pipeline_item)
                            elif item.action == 'update':
                                pipeline_item.quantity = item.quantity
                                pipeline_item.discount = item.discount
                                pipeline_item.save()
                    except (Item.DoesNotExist, ItemVariation.DoesNotExist):
                        return cls(pipeline=None, success=False, message="Invalid item or variant")
            pipeline.save()
            return cls(pipeline=pipeline, success=True, message="Pipeline updated successfully")
        except Exception as e:
            return cls(pipeline=None, success=False, message=f"An error occurred while updating pipeline: {str(e)}")


class MakeOrder(graphene.Mutation):

    class Arguments:
        input = MakeOrderInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    order = graphene.Field(CreateOrderRes)

    @classmethod
    def mutate(cls, root, info, input: MakeOrderInput):
        user = info.context.user
        if not user.is_authenticated:
            raise UnAuthorizedException()

        try:
            pipeline = CheckoutPipeline.objects.get(
                id=input.pipeline_id, user=user)
        except CheckoutPipeline.DoesNotExist:
            raise InvalidModelIdException(model="Checkout Pipeline")

        try:
            shipping_address = user.addresses.get(id=input.shipping_address)
            billing_address = user.addresses.get(id=input.billing_address)
            if not shipping_address or not billing_address:
                raise Exception('Invalid shipping or billing address')
        except:
            return cls(order=None, success=False, message="Invalid shipping or billing address")

        try:
            order = Order(
                user=user,
                total=Decimal(0),
                payment_method=input.payment_method.value or 'other',
                shipping_address=shipping_address,
                billing_address=billing_address,
            )
            order.save()
        except Exception as e:
            return cls(order=None, success=False, message="An error occurred while creating order")

        try:
            for pipeline_item in pipeline.items.all():
                order_item = OrderItem(
                    order=order,
                    item=pipeline_item.item,
                    quantity=pipeline_item.quantity,
                    price=pipeline_item.item.price,
                    total=(pipeline_item.item.price *
                           pipeline_item.quantity) - (pipeline_item.discount or Decimal(0)),
                )
                order_item.save()
                order.total += order_item.total
                order.save()
                order_item.variants.set(pipeline_item.variants.all())
        except Exception as e:
            print(e)
            order.delete()
            return cls(order=None, success=False, message="An error occurred while creating order items")

        try:
            if order and order.order_id:
                from django.forms.models import model_to_dict

                payment = RazorpayPayments().create_order(user, order)
                if payment and payment['status'] == 'created':
                    state_data = {
                        'pipeline': pipeline.id,
                        'order': order.id,
                        'address': {
                            'shipping': model_to_dict(order.shipping_address),
                            'billing': model_to_dict(order.billing_address)
                        },
                        'items': [
                            {
                                'item': str(model_to_dict(item.item, fields=['key', 'name', 'price', 'compare_price'])),
                                'quantity': item.quantity,
                                'price': str(item.price),
                                'total': str(item.total),
                                'variants': [str(model_to_dict(variant)) for variant in item.variants.all()]
                            }
                            for item in order.items.all()
                        ],
                        'total': str(order.total),
                        'payment': {
                            'method': order.payment_method,
                            'session_id': payment['id'],
                        },
                        'promo': pipeline.promotions,
                    }
                    order.state_data = state_data
                    order.save()
                    res = CreateOrderRes()
                    res.payment_session_id = payment['id']
                    res.order_id = order.order_id
                    res.amount = float(order.total)
                    res.status = order.status
                    res.method = order.payment_method
                    res.expiry_time = None
                    return MakeOrder(
                        success=True,
                        message="Order created successfully",
                        order=res
                    )
                else:
                    raise Exception(f'Error creating order with {input.payment_method}.')
        except Exception as e:
            print(e)
            order.delete()
            return cls(order=None, success=False, message="An error occurred while creating order")


class CheckPromoCode(graphene.Mutation):

    class Arguments:
        code = graphene.String(required=True)
        total = graphene.Float(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    promo = graphene.Field(PromoCodeObject)

    @classmethod
    def mutate(cls, root, info, code, total):
        user = info.context.user
        if not user.is_authenticated:
            raise UnAuthorizedException()

        try:
            promo = PromoCode.objects.get(code=code, is_active=True)
        except PromoCode.DoesNotExist:
            return CheckPromoCode(success=False, message="Invalid Promo Code")

        if not promo.is_active:
            return CheckPromoCode(success=False, message="Promo Code is not active")

        if promo.valid_from and promo.valid_from > timezone.now():
            return CheckPromoCode(success=False, message="Promo Code is not valid yet")

        if promo.valid_to and promo.valid_to < timezone.now():
            return CheckPromoCode(success=False, message="Promo Code has expired")

        if promo.minimum_order_value and total < promo.minimum_order_value:
            return CheckPromoCode(success=False, message="Minimum order value not met")

        return CheckPromoCode(success=True, message="Promo Code is valid", promo=promo)
    

class AddRazorPayRes(graphene.Mutation):
    
    class Arguments:
        input = RazoryPayPaymentInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    is_verified = graphene.Boolean()
    order = graphene.Field(OrderObject)
    status = graphene.String()

    @classmethod
    def mutate(cls, root, info, input: RazoryPayPaymentInput):
        user = info.context.user
        if not user.is_authenticated:
            raise UnAuthorizedException()
        try:
            order = Order.objects.get(order_id=input.server_order_id)
        except Order.DoesNotExist:
            return cls(success=False, message="Order not found", is_verified=False, status='failed')
        try:
            payload = {
                'razorpay_order_id': input.order_id,
                'razorpay_payment_id': input.payment_id,
                'razorpay_signature': input.signature
            }
            payment = RazorpayPayments().verify_signature(payload)
            if payment:
                order.payment_status = 'paid'
                order.status = 'confirmed'
                order.extra = payload
                order.save()
                return cls(success=True, message="Payment successful", is_verified=True, order=order, status='paid')
            else:
                return cls(success=True, message="Payment Verification failed", is_verified=False, status='failed')
        except Exception as e:
            return cls(success=False, message="Payment failed", is_verified=False, status='failed')


'''********** Query **********'''


class Query(graphene.ObjectType):
    items = DjangoFilterConnectionField(ItemObject)
    categories = DjangoFilterConnectionField(CategoryObject)
    orders = DjangoFilterConnectionField(OrderObject)
    order_items = DjangoFilterConnectionField(OrderItemObject)
    inventories = DjangoFilterConnectionField(InventoryObject)
    item_reviews = DjangoFilterConnectionField(ItemReviewObject)
    tags = DjangoFilterConnectionField(TagObject)
    checkout_pipelines = DjangoFilterConnectionField(CheckoutPipelineObject)
    promos = DjangoFilterConnectionField(PromoCodeObject)

    item = graphene.Field(ItemObject, key=graphene.String())
    category = relay.Node.Field(CategoryObject)
    order = relay.Node.Field(OrderObject)
    order_item = relay.Node.Field(OrderItemObject)
    inventory = relay.Node.Field(InventoryObject)
    item_review = relay.Node.Field(ItemReviewObject)
    tag = relay.Node.Field(TagObject)
    checkout_pipeline = graphene.Field(CheckoutPipelineObject, id=graphene.ID())

    def resolve_item(self, info, key):
        try:
            return Item.objects.get(key=key)
        except Item.DoesNotExist:
            return None
            
    def resolve_checkout_pipeline(self, info, id):
        user = info.context.user
        if not user.is_authenticated: return None
        try:
            return CheckoutPipeline.objects.get(id=id, user=user)
        except CheckoutPipeline.DoesNotExist:
            return None


class Mutation(graphene.ObjectType):
    create_item = CreateItem.Field()
    update_item = UpdateItem.Field()
    delete_item = DeleteItem.Field()
    update_item_image = ItemImageUpdate.Field()
    update_item_media = ItemMediaUpdate.Field()

    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()

    create_tag = CreateTag.Field()
    update_tag = UpdateTag.Field()
    delete_tag = DeleteTag.Field()

    create_item_review = CreateItemReview.Field()
    update_item_review = UpdateItemReview.Field()
    delete_item_review = DeleteItemReview.Field()

    create_order = CreateOrder.Field()
    verify_order = VerifyGetOrder.Field()

    create_checkout_pipeline = CreateCheckoutPipeline.Field()
    update_checkout_pipeline = UpdateCheckoutPipeline.Field()
    make_order = MakeOrder.Field()
    apply_promo_code = CheckPromoCode.Field()
    verify_razorpay_res = AddRazorPayRes.Field()
