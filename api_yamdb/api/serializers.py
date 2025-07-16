# api/serializers.py
"""
Приложение api.
Сериализаторы для моделей категорий, жанров, названий произведений,
рецензий, комментариев."""
from rest_framework import serializers
from reviews.models import Category, Genre


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории"""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров"""
    class Meta:
        model = Genre
        fields = ('name', 'slug')
