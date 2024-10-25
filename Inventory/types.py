import graphene

from Common.types import ImageInput

class ItemStatusEnum(graphene.Enum):
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    COMING_SOON = "comming_soon"
    DISCONTINUED = "discontinued"

class FieldTypeEnum(graphene.Enum):
    PARAGRAPH = "paragraph"
    LIST = "list"

class ItemVariantInfoObject(graphene.ObjectType):
    name = graphene.String()
    value = graphene.String()
    available = graphene.Boolean()

class ParagraphFieldData(graphene.ObjectType):
    paragraphs = graphene.List(graphene.String)

class ListFieldData(graphene.ObjectType):
    list = graphene.List(graphene.String)

class TextJsonFieldData(graphene.Union):

    class Meta:
        types = (ParagraphFieldData, ListFieldData )

    @classmethod
    def resolve_type(cls, instance, info):
        print(instance)
        if 'paragraphs' in instance:
            return ParagraphFieldData
        if 'list' in instance:
            return ListFieldData
        return None

class TextJsonFieldObject(graphene.ObjectType):
    title = graphene.String()
    type = graphene.String()
    data = graphene.Field(TextJsonFieldData) 

class ItemExtraFieldData(graphene.InputObjectType):
    name = graphene.String()
    value = graphene.String()

class ItemExtraFieldDataObject(graphene.ObjectType):
    name = graphene.String()
    value = graphene.String()

class ItemExtraFieldObject(graphene.ObjectType):
    title = graphene.String()
    type = graphene.String()
    data = graphene.List(ItemExtraFieldDataObject)

class ItemExtraField(graphene.InputObjectType):
    title = graphene.String(required=True)
    type = graphene.String(required=True)
    data = graphene.List(ItemExtraFieldData, required=True)


class BaseItemInput(graphene.InputObjectType):
    teaser = graphene.String()
    images = graphene.List(ImageInput)
    tags = graphene.List(graphene.String)
    status = graphene.Field(ItemStatusEnum)
    shipping_cost = graphene.Float()
    can_return = graphene.Boolean()
    return_time = graphene.Int()
    return_policy = graphene.String()
    brand = graphene.String()
    extra_fields = graphene.List(ItemExtraField)

class NewItemInput(BaseItemInput):
    sku = graphene.String(required=True)
    name = graphene.String(required=True)
    description = graphene.JSONString(required=True)
    image = ImageInput(required=True)
    price = graphene.Float(required=True)
    category = graphene.String(required=True)
    vendor =  graphene.String(required=True)


class UpdateItemInput(NewItemInput):
    sku = graphene.String()
    name = graphene.String()
    description = graphene.JSONString()
    image = ImageInput()
    price = graphene.Float()
    category = graphene.String()


class CategoryInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String()
    image = ImageInput(required=True)
    parent = graphene.String()
    priority = graphene.Int()

class CategoryUpdateInput(graphene.InputObjectType):
    name = graphene.String()
    description = graphene.String()
    image = ImageInput()
    parent = graphene.String()
    priority = graphene.Int()