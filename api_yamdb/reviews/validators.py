# reviews/validators.py
"""
Приложение reviews.
Реализована проверка года произведения.
"""
from django.core.exceptions import ValidationError
from django.utils import timezone


def year_validator(value):
    if value > timezone.now().year:
        raise ValidationError(
            f'Год {value} не может быть в будущем!'
        )

def score_validator(value):
    if value < 1 or value > 10:
        raise ValidationError(
            f'Оценка {value} должна быть от 1 до 10!'
        )
