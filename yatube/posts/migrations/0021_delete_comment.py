# Generated by Django 2.2.16 on 2022-09-20 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0020_comment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
