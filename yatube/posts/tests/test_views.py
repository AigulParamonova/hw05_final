import shutil
import tempfile

from django import forms
from django.conf import settings
from django.conf.urls import handler404
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Follow, Group, Post, User

User = get_user_model()
USERNAME = 'JonSnow'
USERNAME_2 = 'Ned Stark'
USERNAME_3 = 'Pinky'
GROUP_SLUG = 'ned'
GROUP_TITLE = 'The Stark house'
GROUP_DESC = 'Winter is coming'
POST_TEXT = 'Game of the Thrones'
URL_HOMEPAGE = reverse('index')
GROUP_POSTS = f'/group/{GROUP_SLUG}/'
URL_NEW_POST = reverse('new_post')
URL_PROFILE = f'/{USERNAME}/'
URL_FOLLOW = reverse('follow_index')
PROFILE_FOLLOW = f'/{USERNAME_2}/follow/'
PROFILE_UNFOLLOW = f'/{USERNAME_2}/unfollow/'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.user = User.objects.create_user(username=USERNAME)
        cls.user2 = User.objects.create_user(username=USERNAME_2)
        cls.user3 = User.objects.create_user(username=USERNAME_3)

        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESC
        )

        cls.group2 = Group.objects.create(
            title='The Targaryen house',
            slug='daenerys',
            description='Flame and blood'
        )

        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

        cls.URL_POST = f'/{USERNAME}/{cls.post.id}/'
        cls.URL_POST_EDIT = f'/{USERNAME}/{cls.post.id}/edit/'
        cls.URL_COMMENT = f'/{USERNAME}/{cls.post.id}/comment/'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTest.user)

        self.authorized_follower = Client()
        self.authorized_follower.force_login(PostsViewsTest.user3)

        self.authorized_author = Client()
        self.authorized_author.force_login(PostsViewsTest.user2)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'posts/index.html': URL_HOMEPAGE,
            'posts/new_post.html': URL_NEW_POST,
            'posts/group.html': GROUP_POSTS,
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(URL_HOMEPAGE)
        object = response.context['page'].object_list[0]
        expected_text = object.text
        expected_author = object.author
        expected_image = object.image
        self.assertEqual(expected_text, PostsViewsTest.post.text)
        self.assertEqual(expected_author, PostsViewsTest.user)
        self.assertEqual(expected_image, PostsViewsTest.post.image)

    def test_group_posts_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(GROUP_POSTS)
        object = response.context['group']
        expected_title = object.title
        expected_slug = object.slug
        expected_description = object.description
        self.assertEqual(expected_title, PostsViewsTest.group.title)
        self.assertEqual(expected_slug, PostsViewsTest.group.slug)
        self.assertEqual(
            expected_description, PostsViewsTest.group.description
        )

    def test_group_posts_context_with_image(self):
        """Шаблон group_posts сформирован
        с правильным контекстом и изображением.
        """
        response = self.authorized_client.get(GROUP_POSTS)
        object = response.context['page'].object_list[0]
        expected_image = object.image
        self.assertEqual(
            expected_image,
            PostsViewsTest.post.image
        )

    def test_new_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(URL_NEW_POST)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(URL_PROFILE)
        object = response.context['page'].object_list[0]
        expected_text = object.text
        expected_author = object.author
        expected_image = object.image
        self.assertEqual(expected_text, PostsViewsTest.post.text)
        self.assertEqual(expected_author, PostsViewsTest.user)
        self.assertEqual(expected_image, PostsViewsTest.post.image)

    def test_post_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(PostsViewsTest.URL_POST)
        object = response.context['post']
        expected_text = object.text
        expected_author = object.author
        expected_image = object.image
        self.assertEqual(expected_text, PostsViewsTest.post.text)
        self.assertEqual(expected_author, PostsViewsTest.user)
        self.assertEqual(expected_image, PostsViewsTest.post.image)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(PostsViewsTest.URL_POST_EDIT)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_check_post_in_group_posts(self):
        """
        Новый пост с указанием группы отображается
        в выбранной группе.
        """
        response = self.authorized_client.get(GROUP_POSTS)
        self.assertEqual(response.context['group'].title,
                         PostsViewsTest.group.title)
        self.assertEqual(response.context['group'].slug,
                         PostsViewsTest.group.slug)
        self.assertEqual(response.context['group'].description,
                         PostsViewsTest.group.description)

        object = response.context['page'].object_list[0]
        expected_text = object.text
        expected_group = object.group
        self.assertEqual(expected_text, PostsViewsTest.post.text)
        self.assertEqual(expected_group.title, PostsViewsTest.group.title)

        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'daenerys'})
        )
        assert not response.context['page'].has_next()

    def test_test_check_post_in_index(self):
        """Новый пост с указанием группы отображается на главной странице."""
        response = self.authorized_client.get(URL_HOMEPAGE)
        first_object = response.context['page'].object_list[0]
        post_text = first_object.text
        self.assertEqual(post_text, PostsViewsTest.post.text)

    def test_server_check_error_404(self):
        """Сервер возвращает код 404, если страница не найдена."""
        response = self.authorized_client.get(handler404)
        self.assertEqual(response.status_code, 404)

    def test_index_in_cache_check(self):
        """Посты главной страницы хранятся в кэше."""
        response = self.authorized_client.get(URL_HOMEPAGE)
        post = Post.objects.create(
            text='Тестируем кэш',
            author=PostsViewsTest.user
        )
        page = response.content
        self.assertEqual(page, response.content)
        post.delete()
        response = self.client.get(URL_HOMEPAGE)
        cache.clear()
        self.assertNotEqual(response, response.content)

    def test_auth_follow_check(self):
        """Авторизованный пользователь может подписываться
        на других пользователей и отписываться.
        """
        self.authorized_follower.get(PROFILE_FOLLOW)
        follows = Follow.objects.filter(
            user=PostsViewsTest.user3,
            author=PostsViewsTest.user2
        ).count()
        self.assertEqual(follows, 1)

        self.authorized_follower.get(PROFILE_UNFOLLOW)
        follows = Follow.objects.filter(
            user=PostsViewsTest.user3,
            author=PostsViewsTest.user2
        ).count()
        self.assertNotEqual(follows, 1)

    def test_new_post_check_at_followers(self):
        """Новый пост пользователя появляется у подписчиков и
        не появляется у не подписанных подьзователей.
        """
        self.authorized_follower.get(PROFILE_FOLLOW)
        form_data = {
            'text': 'Тестируем пост у подписчиков',
            'author': PostsViewsTest.user2,
        }
        self.authorized_author.post(
            URL_NEW_POST,
            data=form_data,
            follow=True
        )
        response = self.authorized_follower.get(URL_FOLLOW)
        self.assertContains(response, form_data['text'])
        response = self.authorized_client.get(URL_FOLLOW)
        self.assertNotContains(response, form_data['text'])

    def test_authorized_user_may_comment(self):
        """Авторизированный пользователь может комментировать посты."""
        comment = Comment.objects.count()
        form_data = {
            'post': PostsViewsTest.post,
            'author': PostsViewsTest.user,
            'text': 'Тестовый комментарий',
        }
        self.authorized_client.post(
            PostsViewsTest.URL_COMMENT,
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий',
            ), form_data['text']
        )
