import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from Admin.models import Banner, BannerGroup
from Api import relay
from Common.models import Image,ItemMedia
from Common.tools import ImageUrlBuilder, MediaUrlBuilder
from Common.types import BannerButtonObject

class ImageCropEnum(graphene.Enum):
    SCALE = 'scale'
    FILL = 'fill'

class ImageObject(DjangoObjectType):
    public_id = graphene.String()
    blur_url = graphene.String()
    has_image = graphene.Boolean()
    url = graphene.String(
        width=graphene.Int(),
        height=graphene.Int(),
        crop=graphene.Argument(ImageCropEnum),
        quality=graphene.Int(),
        format=graphene.String(),
        required=True
    )

    class Meta:
        model = Image
        fields = ('url', 'id', 'alt', 'caption', 'provider')

    def resolve_url(self, info, width=None, height=None, crop=None, quality=None, format=None, **kwargs):
        if isinstance(self, Image) and self.has_url:
            return self._url
        return ImageUrlBuilder(self).build_url(
            width=width, height=height, crop=crop.value if crop else None, quality=quality, format=format
        )
    
    def resolve_public_id(self, info):
        return self.url
    
    def resolve_has_image(self, info):
        return self.id is not None
    
    def resolve_blur_url(self, info):
        if self.provider == 'cloudinary' and self.url:
            return ImageUrlBuilder(self).build_url(
                width=10, height=10, crop='fill', quality=10, format='webp', effect={'blur': 200}
            )
        return ImageUrlBuilder(Image(url="74f98fbe6a8ada2db6ec26feb98f994e")).build_url(
            width=10, height=10, crop='fill', quality=10, format='webp', effect={'blur': 200}
        )
    

class ItemMediaObject(DjangoObjectType):
    public_id = graphene.String()
    blur_url = graphene.String()
    has_image = graphene.Boolean()
    url = graphene.String(
        width=graphene.Int(),
        height=graphene.Int(),
        crop=graphene.Argument(ImageCropEnum),
        quality=graphene.Int(),
        format=graphene.String(),
        required=True
    )

    class Meta:
        model = ItemMedia
        fields = ('url', 'id', 'alt', 'type', 'provider')

    def resolve_url(self, info, width=None, height=None, crop=None, quality=None, format=None, **kwargs):
        if isinstance(self, ItemMedia) and self.has_url:
            return self._url
        return MediaUrlBuilder(self).build_url(
            width=width, height=height, crop=crop.value if crop else None, quality=quality, format=format
        )
    
    def resolve_public_id(self, info):
        return self.url
    
    def resolve_has_image(self, info):
        return self.id is not None
    
    def resolve_blur_url(self, info):
        if self.provider == 'cloudinary' and self.url:
            return MediaUrlBuilder(self).build_url(
                width=10, height=10, crop='fill', quality=10, format='webp', effect={'blur': 200}
            )
        return MediaUrlBuilder(ItemMedia(url="74f98fbe6a8ada2db6ec26feb98f994e")).build_url(
            width=10, height=10, crop='fill', quality=10, format='webp', effect={'blur': 200}
        )


class BannerObject(DjangoObjectType):
    button = graphene.Field(BannerButtonObject)

    class Meta:
        model = Banner
        fields = '__all__'
        filter_fields = {
            'id': ['exact'],
            'title': ['exact', 'icontains'],
            'is_active': ['exact'],
            'position': ['exact'],
            'priority': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'created_at': ['exact', 'icontains'],
            'type': ['exact']
        }
        interfaces = (relay.Node, )
        use_connection = True

class BannerGroupObject(DjangoObjectType):
    class Meta:
        model = BannerGroup
        fields = '__all__'
        filter_fields = {
            'id': ['exact'],
            'title': ['exact', 'icontains'],
            'is_active': ['exact'],
            'location': ['exact'],
            'created_at': ['exact', 'icontains']
        }
        interfaces = (relay.Node, )
        use_connection = True

    def resolve_banners(self, info):
        return self.banners.order_by('priority')


class Query(graphene.ObjectType):
    banners = DjangoFilterConnectionField(BannerObject)
    banner = graphene.Field(BannerObject, id=graphene.String())
    banner_groups = DjangoFilterConnectionField(BannerGroupObject)
    banner_group = graphene.Field(BannerGroupObject, id=graphene.String(), location=graphene.String())

    def resolve_banner(self, info, id=None):
        if id:
            return Banner.objects.get(id=id)
        return None
    
    def resolve_banner_group(self, info, id=None, location=None):
        if id:
            return BannerGroup.objects.get(id=id)
        if location:
            return BannerGroup.objects.get(location=location)
        return None

class Mutation(graphene.ObjectType):
    pass