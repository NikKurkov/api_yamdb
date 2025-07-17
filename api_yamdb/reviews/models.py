from django.db import models

from .validators import year_validator


class Category(models.Model):
    """Модель для категории."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        help_text='Выберите категорию'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг',
        db_index=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель для жанра."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        help_text='Выберите жанр'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг',
        db_index=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для названия произведения."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        help_text='Выберите название произведения'
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год',
        db_index=True,
        help_text='Укажите год выпуска',
        null=True,
        blank=True,
        validators=[year_validator]
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание произведения',
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        verbose_name='Жанр',
        help_text='Выберите жанр произведения',
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        help_text='Выберите категорию',
        null=True,
        blank=True,
        related_name='titles'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name
