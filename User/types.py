import graphene
from Common.types import ImageInput


class CustomerInput(graphene.InputObjectType):
    username = graphene.String()
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    sex = graphene.String()
    dob = graphene.Date()
    image = ImageInput()

class BaseUpdateProfileInput(graphene.InputObjectType):
    username = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    sex = graphene.String()
    dob = graphene.Date()
    image = ImageInput()

class SimpliFiedVariantsValues(graphene.ObjectType):
    id = graphene.ID()
    value = graphene.String()

class SimpliFiedVariants(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    values = graphene.List(SimpliFiedVariantsValues)
