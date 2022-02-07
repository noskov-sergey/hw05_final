from django.test import Client, TestCase

TEMPLATES = {
    '/about/author/': 'about/author.html',
    '/about/tech/': 'about/tech.html',
}


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_pages_uses_correct_template(self):
        """При запросе к статичным страницам применяется корректный шаблон."""
        for address, template in TEMPLATES.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
