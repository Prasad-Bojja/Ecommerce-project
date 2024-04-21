# Generated by Django 5.0.2 on 2024-03-12 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceApp', '0025_alter_razorpaytransaction_razor_pay_order_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='codtransaction',
            old_name='cod',
            new_name='cart',
        ),
        migrations.RenameField(
            model_name='razorpaytransaction',
            old_name='rezorpay',
            new_name='cart',
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
