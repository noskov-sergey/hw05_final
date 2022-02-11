import shutil
import tempfile

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Follow, Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

FORM_FIELDS = {
    'text': forms.fields.CharField,
    'group': forms.fields.ChoiceField,
}
TMP_NAME_GLOB = (
    ('posts:index', None, 'posts/index.html'),
    ('posts:post_create', None, 'posts/create_post.html'),
)


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='post_author')
        cls.new_user = User.objects.create_user(username='new_author')
        cls.second_user = User.objects.create_user(username='second_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовая группа',
        )
        cls.group_another = Group.objects.create(
            title='Другая тестовая группа',
            slug='another-slug',
            description='Тестовая группа',
        )
        cls.SMALL_GIF = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded,
        )
        cls.post_another = Post.objects.create(
            author=cls.user,
            text='Другой тестовый пост',
            group=cls.group_another,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.user,
            post=cls.post,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.TMP_NAME = (
            ('posts:group_list', {'slug': self.group.slug},
                'posts/group_list.html'),
            ('posts:profile', {'username': self.user},
                'posts/profile.html'),
            ('posts:post_detail', {'post_id': self.post.id},
                'posts/post_detail.html'),
            ('posts:post_edit', {'post_id': self.post.id},
                'posts/create_post.html'),
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for names, kwargs, template in self.TMP_NAME and TMP_NAME_GLOB:
            with self.subTest(names=names):
                response = self.authorized_client.get(
                    reverse(names, kwargs=kwargs))
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][1].author.username,
            self.post.author.username
        )
        self.assertEqual(response.context['page_obj'][1].text, self.post.text)
        self.assertEqual(
            response.context['page_obj'][1].image, self.post.image)

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug})
        )
        self.assertEqual(
            response.context['page_obj'][0].author.username,
            self.post.author.username
        )
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)
        self.assertEqual(
            response.context['page_obj'][0].group.title, self.post.group.title)
        self.assertEqual(
            response.context['page_obj'][0].image, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                    'username': self.post.author.username})
        )
        self.assertEqual(
            response.context['page_obj'][1].author.username,
            self.post.author.username
        )
        self.assertEqual(response.context['page_obj'][1].text, self.post.text)
        self.assertEqual(
            response.context['page_obj'][1].image, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response.context['post'].author.username,
            self.post.author.username
        )
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(
            response.context['post'].image, self.post.image)
        self.assertEqual(
            response.context['comments'][0].text, self.comment.text)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response.context['post'].author.username,
            self.post.author.username
        )
        self.assertEqual(response.context['post'].text, self.post.text)

    def test_create_post_page_show_correct_context(self):
        """Шаблон формы create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in FORM_FIELDS.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_page_show_correct_posts(self):
        """В шаблон group_list не попадает пост из чужой группы."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug})
        )
        self.assertNotEqual(
            response.context['page_obj'][0].text, self.post_another.text)
        self.assertNotEqual(
            response.context['page_obj'][0].group.title,
            self.post_another.group.title
        )

    def test_follow_and_unfollow_works_good(self):
        """пользователь может подписываться на пользователей и удалять их."""
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.new_user})
        )
        counter = Follow.objects.filter(user=self.user).count()
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={
                    'username': self.second_user})
        )
        counter_follow = Follow.objects.filter(user=self.user).count()
        self.assertEqual(counter_follow, counter + 1)
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={
                    'username': self.second_user})
        )
        counter_unfollow = Follow.objects.filter(user=self.user).count()
        self.assertEqual(counter_unfollow, counter)

    def test_follow_page_show_correct_posts(self):
        """В шаблон follow передаются сообщения follower."""
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.new_user})
        )
        post_new = Post.objects.create(
            author=self.new_user,
            text='Новый тестовый пост follow',
            group=self.group_another,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            response.context['page_obj'][0].author.username,
            post_new.author.username
        )
        self.assertEqual(
            response.context['page_obj'][0].text, post_new.text)

    def test_index_page_cache_works(self):
        """В шаблон index настроено кэширование."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][1].author.username,
            self.post.author.username
        )
        self.assertEqual(response.context['page_obj'][1].text, self.post.text)
        self.assertTrue(Post.objects.filter(text='Тестовый пост').exists())
        Post.objects.filter(text='Тестовый пост').delete()
        self.assertFalse(Post.objects.filter(text='Тестовый пост').exists())
        response_new = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][0].text,
            response_new.context['page_obj'][0].text)
        self.assertEqual(
            response.content, response_new.content)
        cache.clear()
        response_after_clear = self.authorized_client.get(
            reverse('posts:index'))
        self.assertNotEqual(
            response_after_clear.content, response_new.content)


class PaginatorViewsTest(TestCase):
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='post_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовая группа',
        )
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_index_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']), settings.POST_COUNT)

    def test_second_index_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_group_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug})
        )
        self.assertEqual(
            len(response.context['page_obj']), settings.POST_COUNT)

    def test_second_group_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={
                    'slug': self.post.group.slug}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_profile_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                    'username': self.post.author.username})
        )
        self.assertEqual(
            len(response.context['page_obj']), settings.POST_COUNT)

    def test_second_profile_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                    'username': self.post.author.username}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
