from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

User = get_user_model()
USERNAME = 'Rey'
GROUP_SLUG = 'force'
GROUP_TITLE = 'Star Wars'
GROUP_DESC = 'A long time ago in a galaxy far, far away....'
POST_TEXT = 'May the 4th be with you'
URL_HOMEPAGE = reverse('index')
URL_NEW_POST = reverse('new_post')
GROUP_POSTS = f'/group/{GROUP_SLUG}/'
URL_PROFILE = f'/{USERNAME}/'


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESC,
        )

        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user
        )
        cls.URL_POST = f'/{USERNAME}/{cls.post.id}/'
        cls.URL_POST_EDIT = f'/{USERNAME}/{cls.post.id}/edit/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_url_homepage(self):
        """Главная страница доступна любому пользователю."""
        response = self.guest_client.get(URL_HOMEPAGE)
        self.assertEqual(response.status_code, 200)

    def test_url_post_edit_for_guest(self):
        """Страница 'post_edit'недоступна
        для неавторизованного пользователя.
        """
        response = self.guest_client.get(PostsURLTests.URL_POST_EDIT)
        self.assertEqual(response.status_code, 302)

    def test_url_post_edit_for_authorized_client(self):
        """Страница 'post_edit' недоступна
        для авторизованного пользователя.
        """
        response = self.client.get(PostsURLTests.URL_POST_EDIT)
        self.assertEqual(response.status_code, 302)

    def test_url_post_edit_for_author(self):
        """Страница 'post_edit' доступна для автора."""
        response = self.authorized_client.get(PostsURLTests.URL_POST_EDIT)
        self.assertEqual(response.status_code, 200)

    def test_post_edit_redirect_anonymous_on_admin_login(self):
        """Страница 'post_edit' перенаправит
        анонимного пользователя на страницу логина.
        """
        response = self.guest_client.get(
            PostsURLTests.URL_POST_EDIT, follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/Rey/1/edit/'
        )

    def test_url_pages_check(self):
        """Авторизованному пользователю доступны страницы по URL-адресу."""
        url_names = (
            GROUP_POSTS,
            URL_NEW_POST,
            URL_PROFILE,
            PostsURLTests.URL_POST,
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': URL_HOMEPAGE,
            'posts/group.html': GROUP_POSTS,
            'posts/new_post.html': URL_NEW_POST,
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_post_edit_template(self):
        url_name = {
            'posts/new_post.html': PostsURLTests.URL_POST_EDIT,
        }
        for template, url in url_name.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
