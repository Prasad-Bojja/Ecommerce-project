# Generated by Django 5.0.2 on 2024-03-13 13:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceApp', '0028_cart_is_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codtransaction',
            name='cart',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='CODTransaction', to='ecommerceApp.cart'),
        ),
        migrations.AlterField(
            model_name='razorpaytransaction',
            name='cart',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='RazorpayTransaction', to='ecommerceApp.cart'),
        ),
    ]
