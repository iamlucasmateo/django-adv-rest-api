from rest_framework import viewsets, mixins, generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from core.models import Tag, Ingredient
from recipe.serializers import TagSerializer, IngredientSerializer
# Create your views here.


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


# ad hoc view (just for fun)
class IngredientCreateView(generics.CreateAPIView):
    """Creating ingredients, adhoc view"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = IngredientSerializer
    # queryset = Ingredient.objects.all()

    @staticmethod
    def validate_name(name):
        if len(name) == 0:
            raise ValidationError('Invalid name for ingredient')

    def post(self, request):
        """Create a new ingredient"""
        self.validate_name(request.data['name'])
        save_data = dict({
            'user': request.user,
            'name': request.data['name']
        })
        try:
            Ingredient(**save_data).save()
            return Response({
                'message': 'Ingredient created'
            }, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({
                'message': f'Incorrect request body'
            },
                status=status.HTTP_400_BAD_REQUEST
            )
