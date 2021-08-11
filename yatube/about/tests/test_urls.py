from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
