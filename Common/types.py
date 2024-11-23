import graphene

class ImageActionEnum(graphene.Enum):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    NONE = 'none'

class ImageInput(graphene.InputObjectType):
    id = graphene.String()
    url = graphene.String(required=True)
    provider = graphene.String(required=True)
    alt = graphene.String()
    caption  = graphene.String()
    action = ImageActionEnum(required=True)

class MediaInput(graphene.InputObjectType):
    id = graphene.String()
    url = graphene.String(required=True)
    provider = graphene.String(required=True)
    alt = graphene.String()
    type = graphene.String()
    action = ImageActionEnum(required=True)

class BannerButtonObject(graphene.ObjectType):
    text = graphene.String(required=True)
    href = graphene.String()
    color = graphene.String()