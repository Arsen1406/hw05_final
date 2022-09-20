from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

User = get_user_model()


class UserURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()
        self.autorized_client = Client()
        self.user = User.objects.create(username='HasNoName')
        self.autorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/auth/logout/': 'user/logged_out.html',
            '/auth/signup/': 'user/signup.html',
            '/auth/login/': 'user/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/reset/<uidb64>/<token>/':
                'users/password_reset_confirm.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    HTTPStatus(response.status_code).phrase,
                    'OK',
                    f'Проблема с отображением страницы {address}'
                )

    def test_urls_uses_correct_login(self):
        templates_url_names = {
            '/auth/login/': 'user/login.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.autorized_client.get(address)
                self.assertEqual(
                    HTTPStatus(response.status_code).phrase,
                    'OK',
                    f'Проблема с отображением страницы {address}'
                )

    def test_urls_uses_correct_login_change_password(self):
        templates_url_names = {
            '/auth/password_change': 'users/password_change_form.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.autorized_client.get(address)
                self.assertEqual(
                    HTTPStatus(response.status_code).phrase,
                    'Moved Permanently',
                    f'Проблема с отображением страницы {address}'
                )
