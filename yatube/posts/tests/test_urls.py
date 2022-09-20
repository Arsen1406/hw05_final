from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from ..models import Post, Group

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username='HasNoName')
        Post.objects.create(
            text='Тестовый текст',
            author=user
        )
        Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        self.autorized_client = Client()
        self.user = User.objects.get(username='HasNoName')
        self.autorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'post/index.html',
            '/group/test-slug/': 'post/group_list.html',
            '/profile/HasNoName/': 'post/profile.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    HTTPStatus(response.status_code).phrase,
                    'OK',
                    f'Проблема с отображением страницы {address}'
                )

    def test_urls_uses_correct_template_autorized(self):
        post_id = Post.objects.get(text='Тестовый текст')
        templates_url_names = {
            f'/posts/{post_id.id}/': 'post/post_detal.html',
            '/create/': 'post/create_post.html',
            f'/posts/{post_id.id}/edit/': 'post/create_post.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.autorized_client.get(address)
                self.assertEqual(
                    HTTPStatus(response.status_code).phrase,
                    'OK',
                    f'Проблема с отображением страницы {address}'
                )

    def test_urls_uses_correct_template_responce(self):
        post_id = Post.objects.get(text='Тестовый текст')
        templates_url_names = {
            '/create/': 'post/create_post.html',
            f'/posts/{post_id.id}/edit/': 'post/create_post.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    HTTPStatus(response.status_code).phrase,
                    'Found',
                    f'Проблема с отображением страницы {address}'
                )

    def test_urls_uses_correct_404(self):
        response = self.guest_client.get('group/adres')
        self.assertEqual(HTTPStatus(response.status_code).phrase, 'Not Found',
                         'Страница 404 не найдена')
