from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model


class CoreTestPage(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()

    def test_page_not_found(self):
        template_adress = 'index/not_found/'
        response = self.guest_client.get(template_adress)
        self.assertTemplateUsed(response, 'core/404.html')
