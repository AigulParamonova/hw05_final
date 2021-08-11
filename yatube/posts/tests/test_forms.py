import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

USERNAME = 'James'
GROUP_TITLE = 'James Bond'
GROUP_SLUG = 'seven'
GROUP_DESC = 'No Time To Die'
POST_TEXT = 'Bond, James Bond'
URL_HOMEPAGE = reverse('index')
URL_NEW_POST = reverse('new_post')
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESC
        )

        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user
        )
        cls.URL_POST = f'/{USERNAME}/{cls.post.id}/'
        cls.URL_POST_EDIT = f'/{USERNAME}/{cls.post.id}/edit/'
        cls.form = PostForm

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_new_post_create(self):
        """Валидная форма страницы /new/ создает запись в базе данных."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': PostFormTests.post.text,
            'group': PostFormTests.group.id,
            'author': PostFormTests.user,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            URL_NEW_POST,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, URL_HOMEPAGE)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=PostFormTests.post.text,
                group=PostFormTests.group.id,
                author=PostFormTests.user,
                image='posts/small.gif'
            ).first()
        )

    def test_post_edit_creat(self):
        """Валидная форма редактирования поста сохраняется в базе."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'post text edit',
            'group': PostFormTests.group.id,
        }
        response = self.authorized_client.post(
            PostFormTests.URL_POST_EDIT,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PostFormTests.URL_POST)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='post text edit',
                group=PostFormTests.group.id
            ).first
        )
