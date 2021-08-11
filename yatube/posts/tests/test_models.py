from django.test import TestCase

from posts.models import Group, Post, User

USERNAME = 'Harry'
GROUP_TITLE = 'Harry Potter'
GROUP_SLUG = 'hp'
GROUP_DESC = 'Hogwarts'
POST_TEXT = 'Dumbledore'


class PostsModelTest(TestCase):
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

    def test_group(self):
        """В поле __str__  объекта group записано значение поля group.title."""
        group = PostsModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_post(self):
        """В поле __str__  объекта post записано значение поля post.text."""
        post = PostsModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
