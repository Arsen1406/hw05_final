import shutil
import tempfile
from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Post, Group
from django import forms
from django.conf import settings

User = get_user_model()
POST_ID = '1'
POST_TEXT = 'Тестовый пост'
USER_NAME = 'TestUser'
USER_NAME_2 = 'TestUser_2'
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DISCRIPTION = 'Тестовое описание'

TEMLATES_PAGES = {
    reverse('posts:index'): 'posts/index.html',
    (reverse('posts:group', kwargs={'slug': GROUP_SLUG})):
        'posts/group_list.html',
    (reverse('posts:profile', kwargs={'username': USER_NAME})):
        'posts/profile.html',
}


def create_user(username):
    user = User.objects.create_user(username=username)
    return user


def group_create():
    Group.objects.create(
        title=GROUP_TITLE,
        slug=GROUP_SLUG,
        description=GROUP_DISCRIPTION
    )


def post_create(user, img=None):
    Post.objects.create(
        text='Тестовый пост',
        group=Group.objects.get(title=GROUP_TITLE),
        author=user,
        image=img
    )


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().setUpClass()
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
        group_create()
        post_create(create_user(USER_NAME), uploaded)
        post_create(create_user(USER_NAME_2))

    def setUp(self):
        self.guest_client = Client()
        self.autorized_client = Client()
        self.user = User.objects.get(username=USER_NAME)
        self.autorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group', kwargs={'slug': GROUP_SLUG})):
                'posts/group_list.html',
            (reverse('posts:profile', kwargs={'username': USER_NAME})):
                'posts/profile.html',
            (reverse('posts:post_detail', kwargs={'post_id': POST_ID})):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            (reverse('posts:edit', kwargs={'post_id': POST_ID})):
                'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.autorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_correct_context(self):
        response = self.autorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_list_page_show_correct_context(self):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        first_obj = 0
        for reverse_name, template in TEMLATES_PAGES.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.autorized_client.get(reverse_name)
                first_object = response.context['page_obj'][first_obj]
                post_image = Post.objects.first().image
                self.assertEqual(first_object.text,
                                 POST_TEXT,
                                 f'page_obg неверно передается в {template}')
                self.assertEqual(first_object.group.title,
                                 GROUP_TITLE,
                                 f'page_obg неверно передается в {template}')
                self.assertEqual(post_image, 'posts/small.gif')

    def test_posts_correct_context_post_detail(self):
        cache.clear()
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': POST_ID})
        )
        first_object = response.context['post']
        post_image = Post.objects.first().image
        self.assertEqual(first_object.text,
                         POST_TEXT,
                         f'post неверно передается в {response}')
        self.assertEqual(first_object.group.title,
                         GROUP_TITLE,
                         f'post неверно передается в {response}')
        self.assertEqual(
            post_image,
            'posts/small.gif',
            'Картинка передается с ошибкой'
        )

    def test_posts_correct_context_post_edit(self):
        rev_http = reverse('posts:edit', kwargs={'post_id': POST_ID})
        response = self.autorized_client.get(rev_http)
        first_object = response.context['form']
        group = Group.objects.get(pk=first_object.initial['group'])
        self.assertEqual(first_object.initial['text'],
                         POST_TEXT,
                         f'form неверно передается пост в {rev_http}')
        self.assertEqual(group.title,
                         GROUP_TITLE,
                         f'form неверно передается группа в {rev_http}')

    def test_posts_correct_context_post_create_edit_guest(self):
        response_create = self.guest_client.get(reverse('posts:post_create'))
        response_edit = self.guest_client.get(
            reverse('posts:edit', kwargs={'post_id': POST_ID}))
        self.assertEqual(
            HTTPStatus(response_create.status_code).phrase,
            'Found',
            'Не авторизованый пользователь не может создать пост'
        )
        self.assertEqual(
            HTTPStatus(response_edit.status_code).phrase,
            'Found',
            'Не авторизованый пользователь не может менять посты')

    def test_posts_correct_context_post_edit_user_post(self):
        post_id = 2
        response = self.autorized_client.get(
            reverse('posts:edit', kwargs={'post_id': post_id}))
        self.assertEqual(
            HTTPStatus(response.status_code).phrase,
            'Found',
            'Пользователь может редактировать только свои посты'
        )

    def test_comment_guest_user(self):
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': POST_ID
                }
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_new_comment_correct_display(self):
        form_data = {
            'text': 'Тестовый комментарий',
            'author': self.user,
            'post': POST_ID
        }
        response = self.autorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': POST_ID
                }
            ),
            data=form_data,
            follow=True
        )
        self.assertContains(response, 'Тестовый комментарий')

    def test_cache_index(self):
        first_state = self.autorized_client.get(reverse('posts:index'))
        post_1 = Post.objects.get(pk=1)
        post_1.text = 'Измененный текст'
        post_1.save()
        second_state = self.autorized_client.get(reverse('posts:index'))
        self.assertEqual(first_state.content, second_state.content)
        cache.clear()
        third_state = self.autorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_state.content, third_state.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        COUNT_POST = 13
        super().setUpClass()
        group_create()
        user = create_user(USER_NAME)

        for i in range(COUNT_POST):
            post_create(user)

    def setUp(self):
        self.autorized_client = Client()
        self.user = User.objects.get(username=USER_NAME)
        self.autorized_client.force_login(self.user)

    def test_first_page_contains_paginator(self):
        cache.clear()
        ten_pages = 10
        three_pages = 3
        for reverse_name, template in TEMLATES_PAGES.items():
            with self.subTest(reverse_name=reverse_name):
                response_one = self.client.get(reverse_name)
                response_two = self.client.get(
                    f'{reverse_name}?page=2'
                )
                self.assertEqual(
                    len(response_one.context['page_obj']),
                    ten_pages,
                    f'Paginator страницы - 1, '
                    f'{reverse_name} работает не правильно'
                )
                self.assertEqual(
                    len(response_two.context['page_obj']),
                    three_pages,
                    f'Paginator страницы - 2, '
                    f'{reverse_name} работает не правильно'
                )
