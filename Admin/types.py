import graphene

from Common.types import ImageInput


class BannerTypeEnum(graphene.Enum):
    BANNER = 'banner'
    SLIDER = 'slider'

class BannerButtonInput(graphene.InputObjectType):
    text = graphene.String(required=True)
    href = graphene.String()
    color = graphene.String()

class BannerInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    description = graphene.String()
    image = ImageInput(required=True)
    small_image = ImageInput()
    button = BannerButtonInput()
    position = graphene.String()
    priority = graphene.Int()
    type = BannerTypeEnum(required=True)
    is_active = graphene.Boolean()

class BannerUpdateInput(graphene.InputObjectType):
    title = graphene.String()
    description = graphene.String()
    image = ImageInput()
    small_image = ImageInput()
    button = BannerButtonInput()
    position = graphene.String()
    priority = graphene.Int()
    type = BannerTypeEnum()
    is_active = graphene.Boolean()

class BannerGroupInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    description = graphene.String()
    banners = graphene.List(graphene.String, required=True)
    location = graphene.String()
    is_active = graphene.Boolean()

class BannerGroupUpdateInput(graphene.InputObjectType):
    title = graphene.String()
    description = graphene.String()
    banners = graphene.List(graphene.String)
    location = graphene.String()
    is_active = graphene.Boolean()

class PageInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    slug = graphene.String(required=True)
    description = graphene.String()
    is_last = graphene.Boolean()
    parent = graphene.String()
    image = ImageInput()
    content = graphene.String()

class PageUpdateInput(graphene.InputObjectType):
    title = graphene.String()
    slug = graphene.String()
    description = graphene.String()
    is_last = graphene.Boolean()
    parent = graphene.String()
    image = ImageInput()
    content = graphene.String()