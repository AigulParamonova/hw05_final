from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

USERNAME = 'Elon Musk'
GROUP_SLUG = 'elon'
GROUP_TITLE = 'Tesla'
GROUP_DESC = 'And how do you like this, EM?'
URL_HOMEPAGE = reverse('index')
GROUP_POSTS = f'/group/{GROUP_SLUG}/'
URL_NEW_POST = reverse('new_post')
URL_PROFILE = f'/{USERNAME}/'


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)

        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESC
        )

        Post.objects.bulk_create((Post(
            text='Hello', author=cls.user, group=cls.group) for i in range(13))
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTests.user)

    def test_index_page_contains_ten_records(self):
        """На главную страницу передаётся 10 записей."""
        response = self.guest_client.get(URL_HOMEPAGE)
        self.assertEqual(len(response.context['page']), 10)

    def test_group_post_page_contains_ten_records(self):
        """На страницу group_posts передаётся 10 записей."""
        response = self.authorized_client.get(GROUP_POSTS)
        self.assertEqual(len(response.context['page']), 10)

    def test_profile_page1_contains_ten_records(self):
        """На 1 страницу profile передаётся 10 записей."""
        response = self.authorized_client.get(URL_PROFILE)
        self.assertEqual(len(response.context['page']), 10)

    def test_profile_page2_contains_three_records(self):
        """На 2 страницу profile передаётся 3 записи."""
        response = self.authorized_client.get(URL_PROFILE + '?page=2')
        self.assertEqual(len(response.context['page']), 3)
