from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .common import CommonTestCases

User = get_user_model()


class TestRoutes(CommonTestCases):
    @classmethod
    def setUpTestData(cls):
        super().setup_test_data()

    def test_pages_availability_for_anonymous_user(self):
        """Главная страница доступна анонимному пользователю."""
        urls = (
            "notes:home",
            "users:login",
            "users:logout",
            "users:signup",
        )
        for name in urls:
            url = reverse(name)
            response = self.author_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(
                    response.status_code, HTTPStatus.OK, f"URL failed: {url}"
                )

    def test_pages_availability_for_auth_user(self):
        """Аутентифицированному пользователю доступна страница notes"""
        urls = (
            "notes:list",
            "notes:success",
            "notes:add",
        )
        for name in urls:
            url = reverse(name)
            response = self.author_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(
                    response.status_code, HTTPStatus.OK, f"URL failed: {url}"
                )

    def test_pages_availability_for_different_users(self):
        """Другой пользователь — вернётся ошибка 404."""
        users_statuses = (
            (self.author_client, self.author.username, HTTPStatus.OK),
            (self.auth_user_client, self.auth_user.username,
             HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        for client, username, status in users_statuses:
            for name in urls:
                url = reverse(name, args=(self.note.slug,))
                response = client.get(url)
                with self.subTest(username=username, url=url,
                                  expected_status=status):
                    self.assertEqual(response.status_code, status,
                                     f"URL failed for user {username}: {url}")

    def test_redirects(self):
        """Перенаправление на страницу логина."""
        login_url = reverse("users:login")
        urls = (
            ("notes:list", None),
            ("notes:success", None),
            ("notes:add", None),
            ("notes:detail", (self.note.slug,)),
            ("notes:edit", (self.note.slug,)),
            ("notes:delete", (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest():
                url = reverse(name, args=args)
                redirect_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
