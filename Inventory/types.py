from http import server
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
        types = (ParagraphFieldData, ListFieldData, DictFieldData)

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
        if self['weight']:
            return float(self['weight'])
        else:
            return None


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
    vendor = graphene.String(required=True)

class ItemSeoInput(graphene.InputObjectType):
    title = graphene.String()
    description = graphene.String()
    slug = graphene.String()
    keywords = graphene.List(graphene.String)

class ItemShippingInput(graphene.InputObjectType):
    is_physical = graphene.Boolean()
    weight = graphene.Float()
    unit = graphene.String()

class UpdateItemInput(graphene.InputObjectType):
    teaser = graphene.String()
    slug = graphene.String()
    shipping = ItemShippingInput()
    tags = graphene.List(graphene.String)
    status = graphene.Field(ItemStatusEnum)
    can_return = graphene.Boolean()
    return_time = graphene.Int()
    brand = graphene.String()
    extra_fields = graphene.List(ItemExtraField)
    sku = graphene.String()
    name = graphene.String()
    description = graphene.String()
    price = graphene.Float()
    category = graphene.String()
    tax = graphene.Boolean()
    compare_price = graphene.Float()
    cost = graphene.Float()
    seo = ItemSeoInput()


class CategoryInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String()
    image = ImageInput()
    parent = graphene.String()
    priority = graphene.Int()


class CategoryUpdateInput(graphene.InputObjectType):
    name = graphene.String()
    description = graphene.String()
    image = ImageInput()
    parent = graphene.String()
    priority = graphene.Int()


class OrderItemInput(graphene.InputObjectType):
    item = graphene.String(required=True)
    quantity = graphene.Int(required=True)
    price = graphene.Float(required=True)
    total = graphene.Float(required=True)
    variants = graphene.List(graphene.String)


class CreateOrderInput(graphene.InputObjectType):
    items = graphene.List(OrderItemInput, required=True)
    total = graphene.Float(required=True)
    shipping = graphene.Float()
    tax = graphene.Float()
    discount = graphene.Float()
    shipping_address = graphene.String(required=True)
    billing_address = graphene.String(required=True)
    payment_method = graphene.String(required=True)


class CreateOrderRes(graphene.ObjectType):
    payment_session_id = graphene.String(required=True)
    order_id = graphene.String(required=True)
    amount = graphene.Float(required=True)
    status = graphene.String()
    method = graphene.String()
    expiry_time = graphene.String()


class VerifyOrderInput(graphene.InputObjectType):
    order_id = graphene.String(required=True)
    token = graphene.String(required=True)


class PaymentDetailsMetaObject(graphene.ObjectType):
    return_url = graphene.String()


class PaymentDetailsObject(graphene.ObjectType):
    order_id = graphene.String()
    entity = graphene.String()
    order_currency = graphene.String()
    order_amount = graphene.Float()
    order_status = graphene.String()
    payment_session_id = graphene.String()
    order_expiry_time = graphene.String()
    order_note = graphene.String()
    created_at = graphene.String()
    order_splits = graphene.List(graphene.String)
    order_meta = graphene.Field(PaymentDetailsMetaObject)
    order_tags = graphene.String()


class CheckoutPipelineItemInput(graphene.InputObjectType):
    item = graphene.String(required=True)
    quantity = graphene.Int(required=True)
    discount = graphene.Float()
    variants = graphene.List(graphene.String)


class CheckoutPipelineInput(graphene.InputObjectType):
    items = graphene.List(CheckoutPipelineItemInput, required=True)
    promotions = graphene.JSONString()
    order_note = graphene.String()


class CheckoutPipelineItemUpdateActionEnum(graphene.Enum):
    ADD = "add"
    REMOVE = "remove"
    UPDATE = "update"


class CheckoutPipelineItemUpdateInput(graphene.InputObjectType):
    item = graphene.String(required=True)
    quantity = graphene.Int(required=True)
    discount = graphene.Float()
    action = graphene.Field(
        CheckoutPipelineItemUpdateActionEnum, required=True)


class CheckoutPipelineUpdateInput(graphene.InputObjectType):
    items = graphene.List(CheckoutPipelineItemUpdateInput)
    promotions = graphene.JSONString()
    order_note = graphene.String()


class PaymentMethodEnum(graphene.Enum):
    COD = "cod"
    RAZORPAY = "razorpay"
    CASHFREE = "cashfree"
    PAYPAL = "paypal"
    UPI = "upi"
    STRIPE = "stripe"
    PAYTM = "paytm"
    PAYU = "payu"
    GOOGLE_PAY = "google_pay"
    PHONEPE = "phonepe"
    BHIM = "bhim"
    AMAZON_PAY = "amazon_pay"
    APPLE_PAY = "apple_pay"
    SAMSUNG_PAY = "samsung_pay"
    BHARAT_QR = "bharat_qr"
    QR_CODE = "qr_code"
    NET_BANKING = "net_banking"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    EMI = "emi"
    WALLET = "wallet"


class MakeOrderInput(graphene.InputObjectType):
    pipeline_id = graphene.String(required=True)
    total = graphene.Float(required=True)
    shipping = graphene.Float()
    tax = graphene.Float()
    discount = graphene.Float()
    shipping_address = graphene.String(required=True)
    billing_address = graphene.String(required=True)
    payment_method = graphene.Field(PaymentMethodEnum, required=True)


class RazoryPayPaymentInput(graphene.InputObjectType):
    order_id = graphene.String(required=True)
    payment_id = graphene.String(required=True)
    signature = graphene.String(required=True)
    server_order_id = graphene.String(required=True)