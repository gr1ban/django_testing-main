# Стандартная библиотека
from http import HTTPStatus

# Сторонние библиотеки
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

# Локальные импорты приложения
from .conftest import TEXT_COMMENT
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, new_text_comment, news):
    """Анонимный пользователь не может отправить комментарий."""
    Comment.objects.all().delete()
    url = reverse("news:detail", args=(news.id,))
    client.post(url, data=new_text_comment)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, new_text_comment,
                                 news):
    """Авторизованный пользователь может отправить комментарий."""
    Comment.objects.all().delete()
    url = reverse("news:detail", args=(news.id,))
    author_client.post(url, data=new_text_comment)
    assert Comment.objects.count() == 1
    comment = Comment.objects.first()
    assert comment.text == new_text_comment["text"]
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    """Если содержит запрещённые слова, он не будет опубликован."""
    Comment.objects.all().delete()
    bad_words_data = {"text": f"Какой-то текст, {BAD_WORDS[0]}, еще текст"}
    url = reverse("news:detail", args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, form="form", field="text", errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, news, author):
    """Авторизованный пользователь может удалять свои комментарии."""
    Comment.objects.all().delete()

    # Создаем новый комментарий от имени автора
    comment = Comment.objects.create(
        text="Пример комментария",
        news=news,
        author=author
    )

    assert Comment.objects.count() == 1  # Убедимся, что комментарий создан

    news_url = reverse("news:detail", args=(news.id,))
    url_to_comments = reverse("news:delete", args=(comment.id,))
    response = author_client.delete(url_to_comments)
    assertRedirects(response, news_url + "#comments")
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    Comment.objects.all().delete()
    comment.save()
    comment_url = reverse("news:delete", args=(comment.id,))
    response = admin_client.delete(comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, new_text_comment,
                                 news, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    Comment.objects.all().delete()
    comment.save()  # Вновь сохраняем комментарий
    comment_url = reverse("news:edit", args=(comment.id,))
    response = author_client.post(comment_url, data=new_text_comment)
    assertRedirects(response, reverse("news:detail", args=(news.id,)
                                      ) + "#comments")
    fresh_comment = Comment.objects.get(pk=comment.pk)
    assert fresh_comment.text == new_text_comment["text"]


def test_user_cant_edit_comment_of_another_user(
    admin_client, new_text_comment, comment
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    Comment.objects.all().delete()
    comment.save()  # Вновь сохраняем комментарий
    comment_url = reverse("news:edit", args=(comment.id,))
    response = admin_client.post(comment_url, data=new_text_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    fresh_comment = Comment.objects.get(pk=comment.pk)
    assert fresh_comment.text == TEXT_COMMENT  # текст не изменился
