# Generated by Django 5.1.3 on 2024-12-05 12:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_paste_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paste',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pastes', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
    ]