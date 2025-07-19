# api/filters.py
"""
Приложение api.
Реализация фильтрации для произведений.
"""
import django_filters as filters
from reviews.models import Title

class TitleFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__slug')
    genre = filters.CharFilter(field_name='genre__slug', lookup_expr='in') # поддержка ?genre=drama&genre=comedy
    year = filters.NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'year')
