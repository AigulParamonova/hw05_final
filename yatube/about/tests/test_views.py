from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_about_author_accessible_guest_client(self):
        """Страница about/author доступна неавторизованному пользователю."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200)

    def test_page_about_tech_accessible_guest_client(self):
        """Страница about/author доступна неавторизованному пользователю."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, 200)
