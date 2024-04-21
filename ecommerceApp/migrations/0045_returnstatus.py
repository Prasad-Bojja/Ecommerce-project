# Generated by Django 5.0.2 on 2024-03-20 12:50

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceApp', '0044_alter_deliverystatus_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReturnStatus',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('requested', 'Requested'), ('approved', 'Approved'), ('in_transit', 'In Transit'), ('return_received', 'Return Received')], default='requested', max_length=20)),
                ('return_date', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('cart', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='return_status', to='ecommerceApp.cart')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
