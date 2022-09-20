from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post

User = get_user_model()


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
            text='Тестовый пост',
        )

    def test_models_have_correct_objects_name(self):
        """Проверяем, что у моделей корректно работает __str__."""
        task = PostModelTest
        self.assertEqual(task.post.text[:15], self.post.text[:15],
                         'Ошибка создания поста в модели Post')
        self.assertEqual(task.group.title, self.group.title,
                         'Ошибка создания группы в модели Group')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        task = PostModelTest.post

        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expend_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).verbose_name, expend_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        task = PostModelTest.post

        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }

        for field, expend_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).help_text, expend_value
                )
