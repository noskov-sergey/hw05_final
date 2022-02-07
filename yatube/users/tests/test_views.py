from django.contrib.auth.forms import UsernameField
from django.contrib.auth.tokens import default_token_generator
from django.forms.fields import CharField, EmailField
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from posts.models import User

FORM_FIELDS = {
    'first_name': CharField,
    'last_name': CharField,
    'username': UsernameField,
    'email': EmailField,
}
TEMPLATE_PAGES_NAME_GLOBAL = (
    ('users:signup', 'users/signup.html'),
    ('users:login', 'users/login.html'),
    ('users:password_reset_form', 'users/password_reset_form.html'),
    ('users:password_reset_done', 'users/password_reset_done.html'),
    ('users:password_reset_complete', 'users/password_reset_complete.html'),
    ('users:password_change_form', 'users/password_change_form.html'),
    ('users:password_change_done', 'users/password_change_done.html'),
    ('users:logout', 'users/logged_out.html'),
)


class AuthPagesTests(TestCase):
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_template_users_works(self):
        """View функция использует соответствующий шаблон."""
        for names, template in TEMPLATE_PAGES_NAME_GLOBAL:
            with self.subTest(names=names):
                response = self.authorized_client.get(
                    reverse(names))
                self.assertTemplateUsed(response, template)

    def test_users_context(self):
        """Шаблон формы signup сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('users:signup'))
        for value, expected in FORM_FIELDS.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_page_show_correct_context(self):
        """Шаблон формы signup сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('users:password_reset_confirm',
                    kwargs={'uidb64': urlsafe_base64_encode(
                        force_bytes(self.user)),
                        'token': default_token_generator.make_token(
                            self.user)}))
        self.assertTemplateUsed(response, 'users/password_reset_confirm.html')
