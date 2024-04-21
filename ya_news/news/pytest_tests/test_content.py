from django.conf import settings
from django.urls import reverse
import pytest

from ..forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, list_news):
    """Количество новостей на главной странице — не более 10."""
    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context["object_list"]
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, list_news):
    """Новости отсортированы от самой свежей к самой старой."""
    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context["object_list"]
    all_news = [news for news in object_list]
    sorted_news = sorted(all_news, key=lambda x: x.date, reverse=True)
    assert sorted_news == list_news


@pytest.mark.django_db
def test_comments_order(client, news, list_comments):
    """Комментарии, старые в начале списка, новые — в конце."""
    url = reverse("news:detail", args=(news.id,))
    response = client.get(url)
    assert "news" in response.context
    news = response.context["news"]
    all_comments = news.comment_set.all()
    assert all(
        all_comments[i].created < all_comments[i + 1].created
        for i in range(len(all_comments) - 1)
    )


@pytest.mark.parametrize(
    "parametrized_client, status",
    (
        (pytest.lazy_fixture("client"), False),
        (pytest.lazy_fixture("author_client"), True),
    ),
)
@pytest.mark.django_db
def test_anonymous_client_has_no_form(parametrized_client, status, comment):
    """Анонимному пользователю недоступна форма для отправки комментария."""
    url = reverse("news:detail", args=(comment.id,))
    response = parametrized_client.get(url)
    has_form = "form" in response.context and isinstance(
        response.context["form"], CommentForm
    )
    assert has_form is status
