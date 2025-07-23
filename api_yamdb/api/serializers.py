# api/serializers.py
"""
Приложение api.
Сериализаторы для моделей категорий, жанров, названий произведений,
рецензий, комментариев.
"""
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Genre, Title, Review, Comment
from reviews.validators import year_validator


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=256,
        error_messages={
            'max_length': 'Длина поля `name` должна быть ограничена 256 символами',
        }
    )
    slug = serializers.SlugField(
        max_length=50,
        error_messages={
            'max_length': 'Длина поля `slug` должна быть ограничена 50 символами',
            'invalid': (
                'Поле `slug` может содержать только буквы латиницы, цифры, '
                'дефисы и подчёркивания'
            ),
        },
        validators=[
            UniqueValidator(
                queryset=Category.objects.all(),
                message='Категория с таким slug уже существует'
            )
        ]
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров"""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для названий произведений (чтение)"""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year',
            'description', 'rating',
            'genre', 'category'
        )

    def get_description(self, obj):
        """
        Возвращает description.
        Если в базе description = NULL, возвращаем пустую строку.
        """
        return obj.description or ""

    def get_rating(self, obj):
        """
        Возвращает средний `score` всех отзывов или `None`, если их нет.
        """
        return obj.reviews.aggregate(avg=Avg('score'))['avg']


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для названий произведений (запись)"""
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )
    year = serializers.IntegerField(
        required=True,
        validators=[year_validator]
    )

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre')

    def validate_genre(self, value):
        """
        Запрещаем создавать Title без жанров.
        """
        if not value:
            raise serializers.ValidationError(
                'Поле `genre` не может быть пустым.'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для рецензий."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    score = serializers.IntegerField()
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate(self, value):
        author = self.context['request'].user
        title_id = (self.context['request'].
                    parser_context['kwargs'].get('title_id'))
        title = get_object_or_404(
            Title,
            id=title_id
        )
        if (self.context['request'].method == 'POST'
            and title.reviews.filter(author=author).exists()):
            raise serializers.ValidationError(
                f'Отзыв на произведение {title.name} уже существует'
            )
        return value

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев"""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment
