# Generated by Django 3.1.6 on 2022-04-14 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0009_auto_20220413_2253'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='patment_completed',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Cash On Delivery', 'Cash On Delivery'), ('Khalti', 'khalti')], default='Cash On Delivery', max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('Order Processing', 'Order Processing'), ('On the way', 'On the way'), ('Order Canceled', 'Order Canceled'), ('Order Received', 'Order Received'), ('Order Completed', 'Order Completed')], max_length=50),
        ),
    ]
