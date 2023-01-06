# Generated by Django 2.2.28 on 2023-01-04 14:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('OmniDB_app', '0003_userdetails_masterpass_check'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('config_snapshot', models.TextField()),
                ('commit_comment', models.TextField(blank=True)),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='OmniDB_app.Connection')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
