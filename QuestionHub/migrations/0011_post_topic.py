# Generated by Django 5.0.1 on 2024-02-07 22:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuestionHub', '0010_rename_topic_name_topic_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='topic',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='QuestionHub.topic'),
        ),
    ]
