from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class AboutURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_template(self):
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    HTTPStatus(response.status_code).phrase,
                    'OK',
                    f'Проблема с отображением страницы {address}'
                )


class AboutViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        response_revers = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

        for reverse_name, template in response_revers.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    HTTPStatus(response.status_code).phrase,
                    'OK',
                    f'Проблема с отображением страницы {reverse_name}'
                )

        for reverse_name, template in response_revers.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
