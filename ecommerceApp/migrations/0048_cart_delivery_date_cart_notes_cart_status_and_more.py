# Generated by Django 5.0.2 on 2024-03-20 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceApp', '0047_remove_deliverystatus_return_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='delivery_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cart',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cart',
            name='status',
            field=models.CharField(choices=[('ORDER_RECEIVED', 'Order Received'), ('ORDER_PICKED', 'Order Picked'), ('ORDER_IN_TRANSIT', 'Order In Transit'), ('OUT_FOR_DELIVERY', 'Out For Delivery'), ('ORDER_DELIVERED', 'Order Delivered')], default='ORDER_RECEIVED', max_length=20),
        ),
        migrations.DeleteModel(
            name='DeliveryStatus',
        ),
    ]