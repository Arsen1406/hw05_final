import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from ..forms import PostForm
from django.contrib.auth import get_user_model
from ..models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        User.objects.create_user(username='TestUser')
        Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )

        cls.form = PostForm()

    def setUp(self):
        self.autorized_client = Client()
        self.user = User.objects.get(username='TestUser')
        self.autorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()

        form_data = {
            'text': 'Текст поста',
            'group': 'Группы',
        }

        Post.objects.create(
            text='Тестовый пост',
            group=Group.objects.get(title='Тестовая группа'),
            author=self.user
        )

        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response,
                             f'{reverse("users:login")}?next=/create/')
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост',
            ).exists()
        )

    def test_edit_post(self):
        Post.objects.create(
            text='Тестовый пост',
            group=Group.objects.get(title='Тестовая группа'),
            author=self.user
        )
        count_post = Post.objects.count()
        form_data = {
            'text': 'Новый текст'
        }

        response = self.autorized_client.post(
            reverse(
                'posts:edit', kwargs={
                    'post_id': '1'
                }
            ),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            "posts:post_detail", kwargs={
                "post_id": '1'
            }
        ))
        self.assertEqual(Post.objects.count(), count_post)

    def test_post_with_picture(self):
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
        form_data = {
            'text': 'Пост с картинкой',
            'group': 1,
            'image': uploaded
        }
        self.autorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(text='Пост с картинкой')
        self.assertEqual(post.text, 'Пост с картинкой')
