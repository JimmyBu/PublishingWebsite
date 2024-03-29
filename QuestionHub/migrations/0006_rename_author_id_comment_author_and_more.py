# Generated by Django 5.0.1 on 2024-01-22 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('QuestionHub', '0005_rename_topictag_topic'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='author_id',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='parent_comment_id',
            new_name='parent_comment',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='post_id',
            new_name='post',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='author_id',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='topic',
            old_name='post_id',
            new_name='post',
        ),
    ]
