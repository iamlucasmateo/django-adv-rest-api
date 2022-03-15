from rest_framework import viewsets, mixins, generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from core.models import Tag, Ingredient
from recipe.serializers import TagSerializer, IngredientSerializer
# Create your views here.


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Manage tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        """Return tags for authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new tag
        
        These hooks (perform_create, perform_update, perform_destroy) are
        particularly useful for setting attributes that are implicit in the request,
        but are not part of the request data. For instance, you might 
        set an attribute on the object based on the request user,
        or based on a URL keyword argument.
        Also used for: doing something after object creation (e.g., sending
        an email) or raising Validation Errors
        """
        serializer.save(user=self.request.user)


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin):
    """Manage ingredients"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        """Return ingredients for current user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
    
    # this would be another way to generate a CreateView (same endpoint)
    # def perform_create(self, serializer):
    #     """Creates new ingredient"""
    #     serializer.save(user=self.request.user)


class IngredientCreateView(generics.CreateAPIView):
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
        except Exception as e:
            return Response({
                'message': f'Incorrect request body'
            },
                status=status.HTTP_400_BAD_REQUEST
            )

