# Generated by Django 5.0.1 on 2024-02-23 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecapp', '0002_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='images/'),
        ),
    ]