# Generated by Django 5.0.2 on 2024-04-01 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceApp', '0064_contactus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactus',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
