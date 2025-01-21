# Generated by Django 5.1.2 on 2025-01-21 16:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_profile_profile_picture'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSecurityProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ('two_factor_secret', models.CharField(blank=True, max_length=32, null=True)),
                ('two_factor_enabled', models.BooleanField(default=False)),
                ('backup_codes', models.JSONField(blank=True, default=list)),
                ('failed_login_attempts', models.IntegerField(default=0)),
                ('last_failed_login', models.DateTimeField(blank=True, null=True)),
                ('account_locked_until', models.DateTimeField(blank=True, null=True)),
                ('password_last_changed', models.DateTimeField(auto_now_add=True)),
                ('require_password_change', models.BooleanField(default=False)),
                ('notify_on_login', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Security Profile',
                'verbose_name_plural': 'User Security Profiles',
            },
        ),
    ]
