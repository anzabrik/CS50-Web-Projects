# Generated by Django 4.2.2 on 2023-07-19 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_listing_image_alter_listing_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.CharField(blank=True, max_length=400),
        ),
    ]