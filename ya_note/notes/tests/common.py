from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client
from notes.models import Note

User = get_user_model()


class CommonTestCases(TestCase):
    @classmethod
    def setup_common(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.auth_user = User.objects.create(username='auth_user')
        cls.auth_user_client = Client()
        cls.auth_user_client.force_login(cls.auth_user)

    @classmethod
    def setup_test_data(cls):
        cls.setup_common()
        cls.default_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'author': cls.author
        }
        cls.note = Note.objects.create(**cls.default_data)

    @classmethod
    def setup_alternative(cls):
        cls.setup_common()
        cls.default_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.data = cls.default_data
