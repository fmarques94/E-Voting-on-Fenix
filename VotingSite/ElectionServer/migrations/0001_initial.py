# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-13 19:20
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('answer', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Ballot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ballot', models.TextField()),
                ('publicCredential', models.TextField()),
                ('SBT', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('startDate', models.DateTimeField()),
                ('endDate', models.DateTimeField()),
                ('openCastTime', models.TimeField(null=True)),
                ('closeCastTime', models.TimeField(null=True)),
                ('cryptoParameters', models.TextField()),
                ('publicKey', models.TextField()),
                ('hybrid', models.BooleanField()),
                ('aggregatedEncTally', models.TextField(null=True)),
                ('tally', models.TextField(null=True)),
                ('paperResults', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.TextField()),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ElectionServer.Election')),
            ],
        ),
        migrations.CreateModel(
            name='Trustee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.TextField()),
                ('name', models.TextField()),
                ('email', models.EmailField(max_length=200)),
                ('publicKeyShare', models.TextField()),
                ('partialDecryption', models.TextField(null=True)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ElectionServer.Election')),
            ],
        ),
        migrations.CreateModel(
            name='Voter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.TextField()),
                ('email', models.EmailField(max_length=200)),
                ('publicCredential', models.TextField()),
                ('proofRandomValues', models.TextField(null=True)),
                ('paperVoter', models.BooleanField(default=False)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ElectionServer.Election')),
            ],
        ),
        migrations.CreateModel(
            name='FenixUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(max_length=250)),
                ('email', models.EmailField(max_length=100)),
                ('status', models.CharField(max_length=100)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='election',
            name='admin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ballot',
            name='election',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ElectionServer.Election'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ElectionServer.Question'),
        ),
        migrations.AlterUniqueTogether(
            name='voter',
            unique_together=set([('election', 'identifier')]),
        ),
        migrations.AlterUniqueTogether(
            name='trustee',
            unique_together=set([('election', 'identifier')]),
        ),
        migrations.AlterUniqueTogether(
            name='question',
            unique_together=set([('election', 'question')]),
        ),
        migrations.AlterUniqueTogether(
            name='ballot',
            unique_together=set([('election', 'publicCredential')]),
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together=set([('question', 'answer')]),
        ),
    ]
