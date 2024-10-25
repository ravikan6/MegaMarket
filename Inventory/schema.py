from time import timezone
import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from Admin.models import Brand
from Api import relay
from Common.exceptions import InvalidImageException, InvalidModelIdException, UnAuthorizedException
from Common.models import Image
from Common.tools import ImageHandler
from Inventory.models import Item, Category, Order, OrderItem, Inventory, ItemVariation, ItemReview, Tag
from Inventory.types import CategoryInput, CategoryUpdateInput, ItemExtraFieldObject, ItemVariantInfoObject, NewItemInput, TextJsonFieldData, TextJsonFieldObject, UpdateItemInput
from Vendor.models import Vendor

class ItemObject(DjangoObjectType):
    description = graphene.List(TextJsonFieldObject)
    extra_fields = graphene.List(ItemExtraFieldObject)

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
            'brand': ['exact'],
            'key': ['exact'],
            'sku': ['exact'],
        }
        interfaces= (relay.Node, )
        use_connection = True


    def resolve_description(self, info):
        try:
            if self.description:
                return self.description
            return None
        except:
            return None

class CategoryObject(DjangoObjectType):
    class Meta:
        model = Category
        exclude = ('created_at', 'updated_at')
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces= (relay.Node, )
        use_connection = True


class OrderObject(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'status': ['exact'],
            'created_at': ['exact', 'gt', 'gte', 'lt', 'lte'],
        }
        interfaces= (relay.Node, )
        use_connection = True

class OrderItemObject(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = '__all__'
        filter_fields = {
            'order': ['exact'],
            'item': ['exact'],
            'quantity': ['exact', 'gt', 'gte', 'lt', 'lte'],
        }
        interfaces= (relay.Node, )
        use_connection = True

class InventoryObject(DjangoObjectType):
    class Meta:
        model = Inventory
        fields = '__all__'
        filter_fields = {
            'item': ['exact'],
            'quantity': ['exact', 'gt', 'gte', 'lt', 'lte'],
        }
        interfaces= (relay.Node, )
        use_connection = True

class ItemVariationObject(DjangoObjectType):
    info = graphene.Field(ItemVariantInfoObject)

    class Meta:
        model = ItemVariation
        fields = '__all__'
        interfaces= (relay.Node, )
        use_connection = True


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
        interfaces= (relay.Node, )
        use_connection = True 

class TagObject(DjangoObjectType):
    class Meta:
        model = Tag
        fields = '__all__'
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces= (relay.Node, )
        use_connection = True

'''********** Mutations **********'''

class CreateItem(graphene.Mutation):
    class Input:
        input = NewItemInput(required=True)

    item = graphene.Field(ItemObject)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, input: NewItemInput):
        if not info.context.user.is_authenticated:
            raise UnAuthorizedException()
        elif not info.context.user.type.lower() == 'vendor':
            raise UnAuthorizedException()
        
        try: vendor = Vendor.objects.get(key=input.vendor)
        except Vendor.DoesNotExist: raise InvalidModelIdException(model="Vendor")
        
        try: category = Category.objects.get(id=input.category)
        except Category.DoesNotExist: raise InvalidModelIdException(model="Category")

        brand = None
        if input.brand:
            try: brand = Brand.objects.get(id=input.brand)
            except Brand.DoesNotExist: raise InvalidModelIdException(model="Brand")

        if not vendor or not category: raise InvalidModelIdException(model="Vendor or Category")

        image = ImageHandler(input.image).auto_image()

        if not image or not isinstance(image, Image): raise InvalidImageException()

        item = Item(
            sku=input.sku,
            name=input.name,
            teaser=input.teaser,
            description=input.description,
            image=image,
            status=input.status,
            price=input.price,
            delivery_time=input.delivery_time,
            shipping_cost=input.shipping_cost,
            can_return=input.can_return,
            return_time=input.return_time,
            return_policy=input.return_policy,
            category=category,
            vendor=vendor,
            brand=brand,
            extra_fields=input.extra_fields
        )

        if input.tags:
            for tag in input.tags:
                tag, new = Tag.objects.get_or_create(name=tag)
                item.tags.add(tag)

        if input.images:
            for image in input.images:
                image = ImageHandler(image).auto_image()
                if image and isinstance(image, Image):
                    item.images.add(image)

        item.save()
        return CreateItem(item=item, success=True, message="Item created successfully")

class UpdateItem(graphene.Mutation):

    class Input:
        key = graphene.String(required=True)
        input = UpdateItemInput()

    item = graphene.Field(ItemObject)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, key, input):
        user = info.context.user
        if not user.is_authenticated or not user.is_vendor:
            raise UnAuthorizedException()
        
        try: item = Item.objects.get(key=key)
        except Item.DoesNotExist: raise InvalidModelIdException(model="Item")
        try: 
            if input.sku: item.sku = input.sku
            if input.name: item.name = input.name
            if input.teaser: item.teaser = input.teaser
            if input.description: item.description = input.description
            if input.image:
                item.image = ImageHandler(input.image).auto_image()
            if input.price: item.price = input.price
            if input.category:
                try: item.category = Category.objects.get(id=input.category)
                except Category.DoesNotExist: raise InvalidModelIdException(model="Category")
            if input.vendor:
                pass
            if input.brand:
                try: item.brand = Brand.objects.get(id=input.brand)
                except Brand.DoesNotExist: raise InvalidModelIdException(model="Brand")
            if input.status: item.status = input.status
            if input.shipping_cost: item.shipping_cost = input.shipping_cost
            if type(input.can_return) == bool: item.can_return = input.can_return
            if input.return_time: item.return_time = input.return_time
            if input.return_policy: item.return_policy = input.return_policy
            if input.extra_fields: item.extra_fields = input.extra_fields
            if input.tags:
                for tag in input.tags:
                    tag, new = Tag.objects.get_or_create(name=tag)
                    item.tags.add(tag)
            if input.images:
                for image in input.images:
                    image = ImageHandler(image).auto_image()
                    if image and isinstance(image, Image):
                        item.images.add(image)
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
        
        try: item = Item.objects.get(key=key)
        except Item.DoesNotExist: raise InvalidModelIdException(model="Item")
        
        item.delete()
        return DeleteItem(success=True, message="Item deleted successfully")
    
class CreateCategory(graphene.Mutation):
    class Arguments:
        input = CategoryInput(required=True)

    category = graphene.Field(CategoryObject)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated or not user.is_admin:
            raise UnAuthorizedException()

        _parent = None
        if input.parent: 
            try: _parent = Category.objects.get(id=input.parent)
            except Item.DoesNotExist: raise InvalidModelIdException(model="Parent Category")
        try:
            image = ImageHandler(input.image).auto_image()
            if not image or not isinstance(image, Image): raise InvalidImageException()

            category = Category(
                name=input.name,
                description=input.description,
                image=image,
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

        try: category = Category.objects.get(id=id)
        except Category.DoesNotExist: raise InvalidModelIdException(model="Category")
        
        try:
            if input.name: category.name = input.name
            if input.description: category.description = input.description
            if input.image:
                image = ImageHandler(input.image).auto_image()
                if not image or not isinstance(image, Image): raise InvalidImageException()
                category.image = image
            if input.parent:
                try: category.parent = Category.objects.get(id=input.parent)
                except Category.DoesNotExist: raise InvalidModelIdException(model="Parent Category")
            if input.priority: category.priority = input.priority
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

        try: category = Category.objects.get(id=id)
        except Category.DoesNotExist: raise InvalidModelIdException(model="Category")
        
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

        try: tag = Tag.objects.get(id=id)
        except Tag.DoesNotExist: raise InvalidModelIdException(model="Tag")
        
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

        try: tag = Tag.objects.get(id=id)
        except Tag.DoesNotExist: raise InvalidModelIdException(model="Tag")
        
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
        
        try: item = Item.objects.get(key=item)
        except Item.DoesNotExist: raise InvalidModelIdException(model="Item")

        _variant = None
        if variant:
            try: _variant = ItemVariation.objects.get(id=variant)
            except ItemVariation.DoesNotExist: raise InvalidModelIdException(model="Item Variation")
        
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

        try: review = ItemReview.objects.get(id=id)
        except ItemReview.DoesNotExist: raise InvalidModelIdException(model="Item Review")
        
        try:
            if rating: review.rating = rating
            if review: review.review = review
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

        try: review = ItemReview.objects.get(id=id)
        except ItemReview.DoesNotExist: raise InvalidModelIdException(model="Item Review")
        
        review.delete()
        return DeleteItemReview(success=True, message="Review deleted successfully")
    

'''********** Query **********'''

class Query(graphene.ObjectType):
    items = DjangoFilterConnectionField(ItemObject)
    categories = DjangoFilterConnectionField(CategoryObject)
    orders = DjangoFilterConnectionField(OrderObject)
    order_items = DjangoFilterConnectionField(OrderItemObject)
    inventories = DjangoFilterConnectionField(InventoryObject)
    item_reviews = DjangoFilterConnectionField(ItemReviewObject)
    tags = DjangoFilterConnectionField(TagObject)

    item = graphene.Field(ItemObject, key=graphene.String())
    category = relay.Node.Field(CategoryObject)
    order = relay.Node.Field(OrderObject)
    order_item = relay.Node.Field(OrderItemObject)
    inventory = relay.Node.Field(InventoryObject)
    item_review = relay.Node.Field(ItemReviewObject)
    tag = relay.Node.Field(TagObject)

    def resolve_item(self, info, key):
        try: return Item.objects.get(key=key)
        except Item.DoesNotExist: return None


class Mutation(graphene.ObjectType):
    create_item = CreateItem.Field()
    update_item = UpdateItem.Field()
    delete_item = DeleteItem.Field()

    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()

    create_tag = CreateTag.Field()
    update_tag = UpdateTag.Field()
    delete_tag = DeleteTag.Field()

    create_item_review = CreateItemReview.Field()
    update_item_review = UpdateItemReview.Field()
    delete_item_review = DeleteItemReview.Field()