# Generated by Django 4.1.7 on 2023-03-15 19:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Stadium",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "name",
                    models.CharField(
                        help_text="The name of the stadium", max_length=120
                    ),
                ),
                (
                    "key",
                    models.SlugField(
                        help_text="Unique key, used in URLs and code references",
                        max_length=120,
                        unique=True,
                    ),
                ),
                (
                    "capacity",
                    models.IntegerField(help_text="The full capacity of the stadium"),
                ),
            ],
            options={
                "ordering": ["created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Pitch",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "surface_type",
                    models.CharField(
                        choices=[
                            ("GRASS", "Grass"),
                            ("HYBRID", "Hybrid"),
                            ("ARTIFICIAL", "Artificial"),
                        ],
                        help_text="The type of playing surface",
                        max_length=20,
                    ),
                ),
                (
                    "width",
                    models.PositiveSmallIntegerField(
                        help_text="The width of the playing surface, in CM"
                    ),
                ),
                (
                    "length",
                    models.PositiveSmallIntegerField(
                        help_text="The length of the playing surface, in CM"
                    ),
                ),
                (
                    "stadium",
                    models.OneToOneField(
                        help_text="The stadium that houses this pitch",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="stadiums.stadium",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
                "abstract": False,
            },
        ),
    ]
