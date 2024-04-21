# Стандартные библиотеки
from datetime import datetime, timedelta

# Сторонние библиотеки
import pytest
from django.conf import settings
from django.utils import timezone

# Местные приложения
from news.models import News, Comment


TEXT_COMMENT = 'Текст комментария'
NEW_TEXT_COMMENT = {'text': 'Новый текст'}


@pytest.fixture
def new_text_comment():
    """Новый текст для комментария."""
    return NEW_TEXT_COMMENT


@pytest.fixture
def author(django_user_model):
    """Создаём пользователя."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    """Создаём автора новости в новом клиенте."""
    from django.test import Client
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news():
    """Создаём новость."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
        date=datetime.today(),
    )
    return news


@pytest.fixture
def comment(news, author):
    """Создаём коммент."""
    comment = Comment.objects.create(
        text=TEXT_COMMENT,
        news=news,
        author=author
    )
    return comment


@pytest.fixture
def list_news():
    """Создаём список новостей."""
    today, list_news = datetime.today(), []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        news = News.objects.create(
            title=f'Новость {index}',
            text='Текст новости',
        )
        news.date = today - timedelta(days=index)
        news.save()
        list_news.append(news)
    return list_news


@pytest.fixture
def list_comments(news, author):
    """Создаём список комментариев."""
    now, list_comment = timezone.now(), []
    for index in range(2):
        comment = Comment.objects.create(
            text=f'Текст {index}',
            news=news,
            author=author,
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        list_comment.append(comment)
