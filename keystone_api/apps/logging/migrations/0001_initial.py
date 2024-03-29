# Generated by Django 4.2.7 on 2024-03-12 17:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AppLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('level', models.CharField(max_length=10)),
                ('pathname', models.CharField(max_length=260)),
                ('lineno', models.IntegerField()),
                ('message', models.TextField()),
                ('func', models.CharField(blank=True, max_length=80, null=True)),
                ('sinfo', models.TextField(blank=True, null=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RequestLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.CharField(max_length=100, null=True)),
                ('response_code', models.PositiveSmallIntegerField()),
                ('method', models.CharField(max_length=10, null=True)),
                ('remote_address', models.CharField(max_length=40, null=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('body_response', models.TextField()),
                ('body_request', models.TextField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
