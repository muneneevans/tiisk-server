# Generated by Django 2.0.3 on 2018-07-05 07:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20180523_1229'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordRecoveryToken',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('token', models.CharField(max_length=6, unique=True)),
                ('time_generated', models.DateTimeField(auto_now_add=True)),
                ('is_expired', models.BooleanField(default=False)),
                ('time_activated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
