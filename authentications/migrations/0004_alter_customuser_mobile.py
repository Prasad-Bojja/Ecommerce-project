# Generated by Django 5.0.2 on 2024-04-03 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentications', '0003_customuser_address_customuser_mobile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='mobile',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
