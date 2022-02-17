# Generated by Django 4.0.1 on 2022-02-14 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_link_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='link',
            name='user',
        ),
        migrations.AddField(
            model_name='link',
            name='email',
            field=models.EmailField(default="None", max_length=200),
            preserve_default=False,
        ),
    ]
