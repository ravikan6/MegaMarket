import graphene
from User.schema import Query as UserQuery, Mutation as UserMutation
from Common.schema import Query as CommonQuery, Mutation as CommonMutation
from Inventory.schema import Query as InventoryQuery, Mutation as InventoryMutation
from Admin.schema import Query as AdminQuery, Mutation as AdminMutation
from Vendor.schema import Query as VendorQuery, Mutation as VendorMutation


class Query(UserQuery, CommonQuery, InventoryQuery, AdminQuery, VendorQuery):
    greet = graphene.String(name=graphene.String(default_value="stranger"))
    
    def resolve_greet(self, info, name = None):
        return f'Hello {name}!'

class Mutation(UserMutation, CommonMutation, InventoryMutation, AdminMutation, VendorMutation):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)