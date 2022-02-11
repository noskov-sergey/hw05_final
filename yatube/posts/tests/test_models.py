from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User

FIELDS_VERBOSE_POST = {
    'text': 'Текст поста',
    'created': 'Дата публикации',
    'author': 'автор',
    'group': 'группа',
}
FIELDS_VERBOSE_COMMENT = {
    'post': 'Пост',
    'author': 'Автор',
    'text': 'Текст комментария',
}
FIELDS_HELPS_POST = {
    'text': 'Сообщение',
    'group': 'Группа, которой пренадлежит пост',
}
FIELDS_VERBOSE_FOLLOW = {
    'user': 'Подписчик',
    'author': 'Подписка на',
}
FIELDS_HELPS_FOLLOW = {
    'user': 'Подписчик',
    'author': 'Подписка на',
}


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_oleg = User.objects.create_user(username='Олег')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый коммент',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_oleg,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_object_name_post = self.post.text[:15]
        self.assertEqual(expected_object_name_post, str(self.post))
        group = PostModelTest.group
        expected_object_name_group = group.title
        self.assertEqual(expected_object_name_group, str(group))

    def test_verbose_name(self):
        """verbose_name post в полях совпадает с ожидаемым."""
        for field, expected_value in FIELDS_VERBOSE_POST.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_verbose_name(self):
        """verbose_name comment в полях совпадает с ожидаемым."""
        for field, expected_value in FIELDS_VERBOSE_COMMENT.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        for field, expected_value in FIELDS_HELPS_POST.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)

    def test_verbose_name(self):
        """verbose_name follow в полях совпадает с ожидаемым."""
        for field, expected_value in FIELDS_VERBOSE_FOLLOW.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.follow._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """help_text follow в полях совпадает с ожидаемым."""
        for field, expected_value in FIELDS_HELPS_FOLLOW.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.follow._meta.get_field(field).help_text,
                    expected_value
                )
