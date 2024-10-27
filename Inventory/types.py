import graphene

from Common.types import ImageInput

class ItemStatusEnum(graphene.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"

class FieldTypeEnum(graphene.Enum):
    PARAGRAPH = "paragraph"
    LIST = "list"
    DICT = "dict"

class ItemVariantInfoObject(graphene.ObjectType):
    name = graphene.String()
    value = graphene.String()
    available = graphene.Boolean()

class ItemSeoObject(graphene.ObjectType):
    title = graphene.String()
    description = graphene.String()
    keywords = graphene.List(graphene.String)

class ItemSeoInput(graphene.InputObjectType):
    title = graphene.String()
    description = graphene.String()
    slug = graphene.String()
    keywords = graphene.List(graphene.String)

class ParagraphFieldData(graphene.ObjectType):
    paragraph = graphene.String()

class ListFieldData(graphene.ObjectType):
    list = graphene.List(graphene.String)

class DictFieldDataDict(graphene.ObjectType):
    key = graphene.String()
    value = graphene.String()

class DictFieldData(graphene.ObjectType):
    dict = graphene.List(DictFieldDataDict)

class TextJsonFieldData(graphene.Union):

    class Meta:
        types = (ParagraphFieldData, ListFieldData, DictFieldData )

    @classmethod
    def resolve_type(cls, instance, info):
        print(instance)
        if 'paragraph' in instance:
            return ParagraphFieldData
        if 'list' in instance:
            return ListFieldData
        if 'dict' in instance:
            return DictFieldData
        return None

class TextJsonFieldObject(graphene.ObjectType):
    title = graphene.String()
    type = graphene.String()
    data = graphene.Field(TextJsonFieldData) 

class ShippingInfoObject(graphene.ObjectType):
    is_physical = graphene.Boolean()
    weight = graphene.Float()
    unit = graphene.String()

    def resolve_weight(self, info):
        if self.weight:
            return float(self.weight)
        else: return None

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

class NewItemInput(graphene.InputObjectType):
    vendor =  graphene.String(required=True)


class UpdateItemInput(graphene.InputObjectType):
    teaser = graphene.String()
    slug = graphene.String()
    shipping = graphene.JSONString()
    tags = graphene.List(graphene.String)
    status = graphene.Field(ItemStatusEnum)
    can_return = graphene.Boolean()
    return_time = graphene.Int()
    brand = graphene.String()
    extra_fields = graphene.List(ItemExtraField)
    sku = graphene.String()
    name = graphene.String()
    description = graphene.JSONString()
    price = graphene.Float()
    category = graphene.String()
    tax = graphene.Boolean()
    compare_price = graphene.Float()
    cost = graphene.Float()
    seo = graphene.JSONString()

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