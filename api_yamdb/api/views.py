# api/views.py
"""
Приложение api.
Реализованы функции просмотра категорий, жанров, создания/редактирования
названий произведений, создания/просмотра рецензий,
создания/просмотра комментариев.
"""
from rest_framework import mixins, viewsets, filters
from reviews.models import Category, Genre
from .serializers import CategorySerializer, GenreSerializer
from .permissions import IsAdminOrReadOnly


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CategoryViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
