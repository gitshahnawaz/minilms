# Generated by Django 4.2.16 on 2024-09-27 15:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("courses", "0002_remove_quiz_date_remove_quiz_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="quiz",
            name="teacher",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
