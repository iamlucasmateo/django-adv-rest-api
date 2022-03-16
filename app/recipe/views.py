from rest_framework import viewsets, mixins, generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import (
    RecipeDetailSerializer, TagSerializer, IngredientSerializer, RecipeSerializer
)


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base view set for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return attrs for authenticated users"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Saves object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        """Retrieve recipes for authenticated user"""
        return self.queryset.filter(user=self.request.user)
    
    # use a different serializer for different actions
    def get_serializer_class(self):
        """Return appropiate serializer class"""
        # 'retrieve' action for details
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        return super().get_serializer_class()
    
    # para post, patch y put
    def perform_create(self, serializer):
        """Create a new recipe"""
        return serializer.save(user=self.request.user)

