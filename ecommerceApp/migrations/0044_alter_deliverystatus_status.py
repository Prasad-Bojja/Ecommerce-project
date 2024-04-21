# Generated by Django 5.0.2 on 2024-03-20 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceApp', '0043_deliverystatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliverystatus',
            name='status',
            field=models.CharField(choices=[('ORDER_RECEIVED', 'Order Received'), ('ORDER_PICKED', 'Order Picked'), ('ORDER_IN_TRANSIT', 'Order In Transit'), ('OUT_FOR_DELIVERY', 'Out For Delivery'), ('ORDER_DELIVERED', 'Order Delivered')], default='order_placed', max_length=20),
        ),
    ]
