from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

LINKS = {
    'about:author': HTTPStatus.OK.value,
    'about:tech': HTTPStatus.OK.value,
}
TEMPLATES = {
    'about:author': 'about/author.html',
    'about:tech': 'about/tech.html',
}


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:, доступен."""
        for name, status in LINKS.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, status)

    def test_about_pages_uses_correct_template(self):
        """При запросе к about: применяется корректный шаблон."""
        for name, template in TEMPLATES.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
