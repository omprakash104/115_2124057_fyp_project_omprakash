# Generated by Django 3.1.6 on 2022-04-14 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0013_auto_20220415_0005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('On the way', 'On the way'), ('Order Received', 'Order Received'), ('Order Completed', 'Order Completed'), ('Order Canceled', 'Order Canceled'), ('Order Processing', 'Order Processing')], max_length=50),
        ),
    ]
