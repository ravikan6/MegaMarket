from time import timezone
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from Admin.models import Banner, BannerGroup
from Admin.payments import Payments
from Api import relay
from Common.schema import BannerGroupObject, BannerObject
from Common.tools import ImageHandler
from Admin.types import BannerGroupInput, BannerGroupUpdateInput, BannerInput, BannerUpdateInput, PageInput, PageUpdateInput
from .models import Page


class PageObject(DjangoObjectType):
    class Meta:
        model = Page
        fields = '__all__'
        filter_fields = {
            'slug': ['exact', 'icontains'],
            'title': ['exact', 'icontains'],
            'description': ['exact', 'icontains'],
            'is_last': ['exact'],
            'created_at': ['exact', 'icontains'],
            'updated_at': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )
        use_connection = True


class CreateBanner(graphene.Mutation):
    class Input:
        input = BannerInput(required=True)
    
    banner = graphene.Field(BannerObject)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            raise Exception('You are not authorized to perform this action.')
        image_data = input.pop('image')
        image = ImageHandler(image_data).auto_image()
        if 'small_image' in input:
            small_image_data = input.pop('small_image')
            small_image = ImageHandler(small_image_data).auto_image()
            input['small_image'] = small_image
        banner = Banner.objects.create(image=image, **input)
        return CreateBanner(banner=banner, success=True, message='Banner created successfully.')

class UpdateBanner(graphene.Mutation):
    class Input:
        id = graphene.String(required=True)
        input = BannerUpdateInput(required=True)
    
    banner = graphene.Field(BannerObject)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, id, input):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            raise Exception('You are not authorized to perform this action.')
        banner = Banner.objects.get(id=id)
        if not banner:
            raise Exception(f'Banner with ID {id} does not exist.')
        if 'image' in input:
            image_data = input.pop('image')
            image = ImageHandler(image_data).auto_image()
            banner.image = image
        if 'small_image' in input:
            small_image_data = input.pop('small_image')
            small_image = ImageHandler(small_image_data).auto_image()
            banner.small_image = small_image
        for key, value in input.items():
            if value:
                setattr(banner, key, value)
        banner.is_active = input.get('is_active', banner.is_active)
        banner.updated_at = timezone.now()
        banner.save()
        return UpdateBanner(banner=banner, success=True, message='Banner updated successfully.')
    
class CreateBannerGroup(graphene.Mutation):
    
    class Input:
        input = BannerGroupInput(required=True)

    banner_group = graphene.Field(BannerGroupObject)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            raise Exception('You are not authorized to perform this action.')
        banners = input.pop('banners')
        for banner_id in banners:
            try:
                banner = Banner.objects.get(id=banner_id)
                if banner:
                    input['banners'].add(banner)
            except Banner.DoesNotExist:
                raise Exception(f'Banner with ID {banner_id} does not exist.')
        banner_group = BannerGroup.objects.create(**input)
        return CreateBannerGroup(banner_group=banner_group, success=True, message='Banner group created successfully.')

class UpdateBannerGroup(graphene.Mutation):
        
        class Input:
            id = graphene.String(required=True)
            input = BannerGroupUpdateInput(required=True)
    
        banner_group = graphene.Field(BannerGroupObject)
        success = graphene.Boolean()
        message = graphene.String()
    
        @classmethod
        def mutate(cls, root, info, id, input):
            user = info.context.user
            if not user.is_authenticated or not user.is_staff:
                raise Exception('You are not authorized to perform this action.')
            banner_group = BannerGroup.objects.get(id=id)
            if not banner_group:
                raise Exception(f'Banner group with ID {id} does not exist.')
            if 'banners' in input:
                banners = input.pop('banners')
                for banner_id in banners:
                    try:
                        banner = Banner.objects.get(id=banner_id)
                        if banner:
                            banner_group.banners.add(banner)
                    except Banner.DoesNotExist:
                        raise Exception(f'Banner with ID {banner_id} does not exist.')
            for key, value in input.items():
                if value:
                    setattr(banner_group, key, value)
            banner_group.save()
            return UpdateBannerGroup(banner_group=banner_group, success=True, message='Banner group updated successfully.')

class CreatePage(graphene.Mutation):
    class Input:
        input = PageInput(required=True)

    page = graphene.Field(PageObject)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        user = info.context.user
        if not user.is_authenticated or not user.is_admin:
            raise Exception('You are not authorized to perform this action.')
        parent = input.pop('parent')
        if parent:
            parent = Page.objects.get(id=parent)
            if not parent:
                raise Exception('Parent page does not exist.')
        image = ImageHandler(input.pop('image')).auto_image()
        page = Page.objects.create(**input, image=image, parent=parent)
        return CreatePage(page=page, success=True, message='Page created successfully.')
    
class UpdatePage(graphene.Mutation):
    class Input:
        id = graphene.String(required=True)
        input = PageUpdateInput(required=True)
    
    page = graphene.Field(PageObject)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, id, input):
        user = info.context.user
        if not user.is_authenticated or not user.is_admin:
            raise Exception('You are not authorized to perform this action.')
        page = Page.objects.get(id=id)
        if not page:
            raise Exception(f'Page with ID {id} does not exist.')
        parent = input.pop('parent')
        if parent:
            parent = Page.objects.get(id=parent)
            if not parent:
                raise Exception('Parent page does not exist.')
        if 'image' in input:
            image = ImageHandler(input.pop('image')).auto_image()
            page.image = image
        for key, value in input.items():
            if value:
                setattr(page, key, value)
        page.parent = parent
        page.save()
        return UpdatePage(page=page, success=True, message='Page updated successfully.')

class Query(graphene.ObjectType):
    pages = DjangoFilterConnectionField(PageObject)
    page = relay.Node.Field(PageObject)

class Mutation(graphene.ObjectType):
    create_banner = CreateBanner.Field()
    update_banner = UpdateBanner.Field()
    create_banner_group = CreateBannerGroup.Field()
    update_banner_group = UpdateBannerGroup.Field()

    create_page = CreatePage.Field()
    update_page = UpdatePage.Field()