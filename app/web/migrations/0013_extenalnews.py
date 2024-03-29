# Generated by Django 3.2.3 on 2021-07-02 03:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailimages", "0023_add_choose_permissions"),
        ("web", "0012_newslistpage_newspage"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExternalNews",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=128)),
                ("published_date", models.DateField()),
                ("url", models.URLField()),
                (
                    "brand_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
        ),
    ]
