# Generated by Django 4.2.2 on 2023-07-21 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_alter_listing_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.URLField(blank=True, max_length=400, null=True),
        ),
    ]