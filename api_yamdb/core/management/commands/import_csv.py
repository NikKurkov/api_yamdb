# core/management/commands/import_csv.py
"""
Модуль импорта данных из csv в СУБД
"""
import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from django.contrib.auth import get_user_model
from reviews.models import Category, Genre, Title, Review, Comment  # наши модели


# Папка с csv-файлами
DATA_DIR = Path('static/data')


def load_csv(filename: str):
    """
    Читает CSV и возвращает список словарей.
    Используем utf‑8.
    """
    with (DATA_DIR / filename).open(encoding='utf-8') as f:
        return list(csv.DictReader(f))


# Команда
class Command(BaseCommand):
    help = 'Импортирует данные из static/data/*.csv в базу.'

    @transaction.atomic  # если что‑то падает – вся сессия откатится
    def handle(self, *args, **options):
        # Порядок вызовов — от независимых таблиц к зависимым.
        self.import_categories()
        self.import_genres()
        self.import_titles()
        self.import_genre_title()
        self.import_users()
        self.import_reviews()
        self.import_comments()

    # Простые справочники
    def import_categories(self):
        rows = load_csv('category.csv')
        objs = [
            Category(id=row['id'], name=row['name'], slug=row['slug'])
            for row in rows
        ]
        Category.objects.bulk_create(objs, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Категорий: {Category.objects.count()}'))

    def import_genres(self):
        rows = load_csv('genre.csv')
        objs = [
            Genre(id=row['id'], name=row['name'], slug=row['slug'])
            for row in rows
        ]
        Genre.objects.bulk_create(objs, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Жанров: {Genre.objects.count()}'))

    # Titles (есть FK на Category)
    def import_titles(self):
        cat_map = {c.id: c for c in Category.objects.all()}
        rows = load_csv('titles.csv')
        objs = [
            Title(
                id=row['id'],
                name=row['name'],
                year=row['year'] or None,
                category=cat_map.get(int(row['category']))
            )
            for row in rows
        ]
        Title.objects.bulk_create(objs, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Произведений: {Title.objects.count()}'))

    # M2M Genre–Title
    def import_genre_title(self):
        title_map = {t.id: t for t in Title.objects.all()}
        genre_map = {g.id: g for g in Genre.objects.all()}
        rows = load_csv('genre_title.csv')
        through_objs = []
        for row in rows:
            title = title_map.get(int(row['title_id']))
            genre = genre_map.get(int(row['genre_id']))
            if title and genre:
                through_objs.append(title.genre.through(title=title, genre=genre))

        title.genre.through.objects.bulk_create(through_objs, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Связи Title–Genre загружены'))

    # Пользователи
    def import_users(self):
        User = get_user_model()
        rows = load_csv('users.csv')
        objs = [
            User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=row.get('role', 'user'),
                password='pbkdf2_sha256$216000$dummy$hash',  # пустой пароль‑заглушка
            )
            for row in rows
        ]
        User.objects.bulk_create(objs, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Пользователей: {User.objects.count()}'))

    # Reviews (FK: title, user)
    def import_reviews(self):
        User = get_user_model()
        title_map = {t.id: t for t in Title.objects.all()}
        user_map = {u.id: u for u in User.objects.all()}

        rows = load_csv('review.csv')
        objs = [
            Review(
                id=row['id'],
                title=title_map.get(int(row['title_id'])),
                text=row['text'],
                author=user_map.get(int(row['author'])),
                score=row['score'],
                pub_date=row['pub_date'],
            )
            for row in rows
        ]
        Review.objects.bulk_create(objs, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Отзывов: {Review.objects.count()}'))

    # Comments (FK: review, user)
    def import_comments(self):
        User = get_user_model()
        review_map = {r.id: r for r in Review.objects.all()}
        user_map = {u.id: u for u in User.objects.all()}

        rows = load_csv('comments.csv')
        objs = [
            Comment(
                id=row['id'],
                review=review_map.get(int(row['review_id'])),
                text=row['text'],
                author=user_map.get(int(row['author'])),
                pub_date=row['pub_date'],
            )
            for row in rows
        ]
        Comment.objects.bulk_create(objs, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Комментариев: {Comment.objects.count()}'))
