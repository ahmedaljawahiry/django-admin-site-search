# Generated by Django 4.1.7 on 2023-03-15 19:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("teams", "0001_initial"),
        ("players", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="playercontract",
            name="team",
            field=models.ForeignKey(
                help_text="The team signing the contract",
                on_delete=django.db.models.deletion.CASCADE,
                to="teams.team",
            ),
        ),
    ]
