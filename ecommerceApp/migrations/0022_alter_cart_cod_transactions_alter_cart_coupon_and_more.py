# Generated by Django 5.0.2 on 2024-03-12 16:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceApp', '0021_codtransaction_razorpaytransaction_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cod_transactions',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_cod_transactions', to='ecommerceApp.codtransaction'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ecommerceApp.coupon'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='razorpay_transactions',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_razorpay_transactions', to='ecommerceApp.razorpaytransaction'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='codtransaction',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='razorpaytransaction',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='razorpaytransaction',
            name='razor_pay_order_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='razorpaytransaction',
            name='razor_pay_payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='razorpaytransaction',
            name='razor_pay_payment_signature',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]