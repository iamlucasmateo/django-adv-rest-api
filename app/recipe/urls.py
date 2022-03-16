from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views, views_old


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredients-list', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
    path('ingredient-create',
         views_old.IngredientCreateView.as_view(),
         name='ingredient-create')
]
