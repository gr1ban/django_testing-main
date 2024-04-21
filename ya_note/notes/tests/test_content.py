from django.urls import reverse

from .common import CommonTestCases


class TestRoutes(CommonTestCases):
    @classmethod
    def setUpTestData(cls):
        super().setup_test_data()

    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.author_client, True),
            (self.auth_user_client, False),
        )
        for user, note_in_list in users_statuses:
            with self.subTest(user=user, note_in_list=note_in_list):
                url = reverse('notes:list')
                response = user.get(url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, note_in_list)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
