# Generated by Django 5.0.2 on 2024-03-15 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceApp', '0036_cart_transaction_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='transaction_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]