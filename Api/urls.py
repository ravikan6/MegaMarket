# Description: This file is used to define the URL patterns for the API application.
from django.urls import path
from graphene_django.views import GraphQLView

version_1 = [
    path('', GraphQLView.as_view(graphiql=True)),
]
