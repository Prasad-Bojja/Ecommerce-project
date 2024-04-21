# Generated by Django 5.0.2 on 2024-03-21 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceApp', '0053_remove_wishlist_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='payment_methods',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='cart',
            name='status',
            field=models.CharField(choices=[('ORDER_RECEIVED', 'Order Received'), ('ORDER_PICKED', 'Order Picked'), ('ORDER_IN_TRANSIT', 'Order In Transit'), ('OUT_FOR_DELIVERY', 'Out For Delivery'), ('ORDER_DELIVERED', 'Order Delivered')], max_length=20),
        ),
    ]