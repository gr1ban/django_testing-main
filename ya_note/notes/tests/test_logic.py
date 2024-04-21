# Стандартная библиотека
from http import HTTPStatus

# Сторонние библиотеки
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

# Локальные модули
from notes.models import Note
from notes.forms import WARNING
from .common import CommonTestCases


User = get_user_model()

URL_NOTE_ADD = 'notes:add'
URL_NOTE_EDIT = 'notes:edit'
URL_NOTE_SUCCESS = 'notes:success'


class TestRoutes(CommonTestCases):
    @classmethod
    def setUpTestData(cls):
        super().setup_alternative()

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        url = reverse(URL_NOTE_ADD)
        response = self.author_client.post(url, data=self.data)
        self.assertRedirects(response, reverse(URL_NOTE_SUCCESS))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.data['title'])
        self.assertEqual(new_note.text, self.data['text'])
        self.assertEqual(new_note.slug, self.data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        url = reverse(URL_NOTE_ADD)
        response = self.client.post(url, self.data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse(URL_NOTE_ADD)
        response = self.author_client.post(url, data={
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': self.note.slug
        })
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Если не заполнен slug, то он формируется автоматически"""
        url = reverse(URL_NOTE_ADD)
        self.data.pop('slug')
        response = self.author_client.post(url, self.data)
        self.assertRedirects(response, reverse(URL_NOTE_SUCCESS))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse(URL_NOTE_SUCCESS))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_user_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse(URL_NOTE_EDIT, args=(self.note.slug,))
        response = self.author_client.post(url, self.data)
        self.assertRedirects(response, reverse(URL_NOTE_SUCCESS))
        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated_note.title, self.data['title'])
        self.assertEqual(updated_note.text, self.data['text'])
        self.assertEqual(updated_note.slug, self.data['slug'])

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse(URL_NOTE_EDIT, args=(self.note.slug,))
        response = self.auth_user_client.post(url, self.data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        unchanged_note = Note.objects.get(pk=self.note.pk)
        self.assertNotEqual(unchanged_note.title, self.data['title'])
        self.assertNotEqual(unchanged_note.text, self.data['text'])
        self.assertNotEqual(unchanged_note.slug, self.data['slug'])
