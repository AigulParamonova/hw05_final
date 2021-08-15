from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User

USERNAME = 'Harry'
USERNAME_2 = 'Ron'
GROUP_TITLE = 'Harry Potter'
GROUP_SLUG = 'hp'
GROUP_DESC = 'Hogwarts'
POST_TEXT = 'Dumbledore'
COMMENT_TEXT = 'Wingardium leviosa'


class PostsModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user2 = User.objects.create_user(username=USERNAME_2)

        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESC
        )

        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=COMMENT_TEXT
        )

        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.user
        )

    def test_group_model(self):
        """В поле __str__  объекта group записано значение поля group.title."""
        group = PostsModelTests.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_post_model(self):
        """В поле __str__  объекта post записано значение поля post.text."""
        post = PostsModelTests.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_comment_model(self):
        """В поле __str__ объекта comment записано значение
        поля comment.text.
        """
        comment = PostsModelTests.comment
        expected_object_name = comment.text
        self.assertEqual(expected_object_name, str(comment))

    def test_follow_model(self):
        """В поле __str__ объекта follow записано значение
        поля follow.user."""
        follow = PostsModelTests.follow
        expected_object_name = follow.user
        self.assertEqual(expected_object_name, follow.user)
