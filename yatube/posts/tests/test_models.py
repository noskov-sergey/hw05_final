from django.test import TestCase

from posts.models import Group, Post, User

FIELDS_VERBOSE = {
    'text': 'Текст поста',
    'created': 'Дата публикации',
    'author': 'Автор',
    'group': 'Группа',
}
FIELDS_HELPS = {

    'text': 'Сообщение',
    'group': 'Группа, которой пренадлежит пост',
}


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_object_name_post = self.post.text[:15]
        self.assertEqual(expected_object_name_post, str(self.post))
        group = PostModelTest.group
        expected_object_name_group = group.title
        self.assertEqual(expected_object_name_group, str(group))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        for field, expected_value in FIELDS_VERBOSE.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        for field, expected_value in FIELDS_HELPS.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)
