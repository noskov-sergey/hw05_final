from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import User

LINKS = {
    '/auth/signup/': HTTPStatus.OK.value,
    '/auth/logout/': HTTPStatus.OK.value,
    '/auth/login/': HTTPStatus.OK.value,
    '/auth/password_reset/': HTTPStatus.OK.value,
    '/auth/password_reset/done/': HTTPStatus.OK.value,
    '/auth/reset/<uidb64>/<token>/': HTTPStatus.OK.value,
    '/auth/reset/done/': HTTPStatus.OK.value,
    '/auth/password_change/': HTTPStatus.FOUND.value,
    '/auth/password_change/done/': HTTPStatus.FOUND.value,
}
TEMPLATES = {
    '/auth/login/': 'users/login.html',
    '/auth/password_reset/': 'users/password_reset_form.html',
    '/auth/password_reset/done/': 'users/password_reset_done.html',
    '/auth/reset/<uidb64>/<token>/': 'users/password_reset_confirm.html',
    '/auth/reset/done/': 'users/password_reset_complete.html',
    '/auth/password_change/': 'users/password_change_form.html',
    '/auth/password_change/done/': 'users/password_change_done.html',
    '/auth/logout/': 'users/logged_out.html',
}


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Auth')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_auth_urls_works(self):
        """Страницы /auth/ доступны."""
        for address, status in LINKS.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_auth_urls_uses_correct_template(self):
        """К страницам модуля auth применяется корректный шаблон."""
        for address, template in TEMPLATES.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
