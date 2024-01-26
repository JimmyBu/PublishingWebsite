# Generated by Django 4.0.3 on 2024-01-23 19:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('QuestionHub', '0006_rename_author_id_comment_author_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DownVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='UpVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='comment',
            name='author',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='comment_number',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='is_nested_comment',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='parent_comment',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='score',
        ),
        migrations.RemoveField(
            model_name='post',
            name='score',
        ),
        migrations.AlterField(
            model_name='comment',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='QuestionHub.post'),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.DeleteModel(
            name='Topic',
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.AddField(
            model_name='upvote',
            name='answer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='QuestionHub.comment'),
        ),
        migrations.AddField(
            model_name='upvote',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upvote', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='downvote',
            name='answer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='QuestionHub.comment'),
        ),
        migrations.AddField(
            model_name='downvote',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downvote', to=settings.AUTH_USER_MODEL),
        ),
    ]
