# Generated by Django 4.1.2 on 2024-12-23 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("episodes", "0007_remove_episode_pass_requirement_out_of_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="episode",
            name="release_version_client",
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
