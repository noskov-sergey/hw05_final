from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User

STATUS_GUEST = {
    '/': HTTPStatus.OK.value,
    '/group/testslug/': HTTPStatus.OK.value,
    '/profile/post_author/': HTTPStatus.OK.value,
    '/create/': HTTPStatus.FOUND.value,
    '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
}
STATUS_AUTH = {
    '/': HTTPStatus.OK.value,
    '/group/testslug/': HTTPStatus.OK.value,
    '/profile/post_author/': HTTPStatus.OK.value,
    '/create/': HTTPStatus.OK.value,
    '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
}
AUTH_TEMPL_URL = {
    '/': 'posts/index.html',
    '/group/testslug/': 'posts/group_list.html',
    '/profile/post_author/': 'posts/profile.html',
    '/create/': 'posts/create_post.html',
}


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='post_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )
        cls.ID_STAT_GUEST = {
            f'/posts/{cls.post.id}/': HTTPStatus.OK.value,
            f'/posts/{cls.post.id}/edit/': HTTPStatus.FOUND.value,
        }
        cls.ID_STAT_VARIA = {
            f'/posts/{cls.post.id}/': HTTPStatus.OK.value,
            f'/posts/{cls.post.id}/edit/': HTTPStatus.OK.value,
        }
        cls.AUTH_TEMPL = {
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()
        self.not_author = User.objects.create_user(username='HasNoName')
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

    def test_urls_for_quest(self):
        """Проверка страниц для неавторизованных пользьзователей."""
        for addr, stat in STATUS_GUEST.items() and self.ID_STAT_GUEST.items():
            with self.subTest(address=addr):
                response = self.guest_client.get(addr)
                self.assertEqual(response.status_code, stat)

    def test_urls_for_authorised(self):
        """Проверка страниц для авторизованных пользьзователей."""
        for addr, stat in STATUS_AUTH.items() and self.ID_STAT_GUEST.items():
            with self.subTest(address=addr):
                response = self.not_author_client.get(addr)
                self.assertEqual(response.status_code, stat)

    def test_urls_for_author(self):
        """Проверка страниц для автора поста."""
        for addr, stat in STATUS_AUTH.items() and self.ID_STAT_VARIA.items():
            with self.subTest(address=addr):
                response = self.authorized_client.get(addr)
                self.assertEqual(response.status_code, stat)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for addr, temp in AUTH_TEMPL_URL.items() and self.AUTH_TEMPL.items():
            with self.subTest(address=addr):
                response = self.authorized_client.get(addr)
                self.assertTemplateUsed(response, temp)
