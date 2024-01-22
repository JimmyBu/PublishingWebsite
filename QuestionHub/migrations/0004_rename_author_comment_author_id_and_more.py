# Generated by Django 5.0.1 on 2024-01-22 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuestionHub', '0003_alter_comment_id_alter_post_id_alter_topictag_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='author',
            new_name='author_id',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='parent_comment',
            new_name='parent_comment_id',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='post',
            new_name='post_id',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='author',
            new_name='author_id',
        ),
        migrations.RenameField(
            model_name='topictag',
            old_name='post',
            new_name='post_id',
        ),
        migrations.AlterField(
            model_name='comment',
            name='id',
            field=models.AutoField(editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='post',
            name='id',
            field=models.AutoField(editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='topictag',
            name='id',
            field=models.AutoField(editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.AutoField(editable=False, primary_key=True, serialize=False),
        ),
    ]
