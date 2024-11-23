from functools import partial

from graphene.types import Interface, Field
from graphene.types.interface import InterfaceOptions
from graphene.relay.node import GlobalID
from graphene.relay.id_type import BaseGlobalIDType, SimpleGlobalIDType
from graphene.types.utils import get_type

class NodeField(Field):
    def __init__(self, node, type_=False, **kwargs):
        assert issubclass(node, Node), "NodeField can only operate in Nodes"
        self.node_type = node
        self.field_type = type_
        global_id_type = node._meta.global_id_type

        super(NodeField, self).__init__(
            # If we don't specify a type, the field type will be the node interface
            type_ or node,
            id=global_id_type.graphene_type(
                required=True, description="The ID of the object"
            ),
            **kwargs,
        )

    def wrap_resolve(self, parent_resolver):
        return partial(self.node_type.node_resolver, get_type(self.field_type))


class AbstractNode(Interface):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, global_id_type=SimpleGlobalIDType, **options):
        assert issubclass(
            global_id_type, BaseGlobalIDType
        ), "Custom ID type need to be implemented as a subclass of BaseGlobalIDType."
        _meta = InterfaceOptions(cls)
        _meta.global_id_type = global_id_type
        _meta.fields = {
            "id": GlobalID(
                cls, global_id_type=global_id_type, description="The ID of the object"
            )
        }
        super(AbstractNode, cls).__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def resolve_global_id(cls, info, global_id):
        return cls._meta.global_id_type.resolve_global_id(info, global_id)


class Node(AbstractNode):
    """An object with an ID"""

    @classmethod
    def Field(cls, *args, **kwargs):  # noqa: N802
        return NodeField(cls, *args, **kwargs)

    @classmethod
    def node_resolver(cls, only_type, root, info, id):
        return cls.get_node_from_global_id(info, id, only_type=only_type)

    @classmethod
    def get_node_from_global_id(cls, info, global_id, only_type=None):
        _type, _id = cls.resolve_global_id(info, global_id)

        graphene_type = info.schema.get_type(_type)
        if graphene_type is None:
            raise Exception(f'Relay Node "{_type}" not found in schema')

        graphene_type = graphene_type.graphene_type

        if only_type:
            assert (
                graphene_type == only_type
            ), f"Must receive a {only_type._meta.name} id."

        # We make sure the ObjectType implements the "Node" interface
        if cls not in graphene_type._meta.interfaces:
            raise Exception(
                f'ObjectType "{_type}" does not implement the "{cls}" interface.'
            )

        get_node = getattr(graphene_type, "get_node", None)
        if get_node:
            return get_node(info, _id)

    @classmethod
    def to_global_id(cls, type_, id):
        return cls._meta.global_id_type.to_global_id(type_, id)