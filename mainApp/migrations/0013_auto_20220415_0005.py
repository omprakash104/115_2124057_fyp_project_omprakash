# Generated by Django 3.1.6 on 2022-04-14 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0012_auto_20220414_2357'),
    ]

    operations = [
        migrations.DeleteModel(
            name='HomeBanner',
        ),
        migrations.DeleteModel(
            name='Slider',
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('Order Processing', 'Order Processing'), ('On the way', 'On the way'), ('Order Received', 'Order Received'), ('Order Canceled', 'Order Canceled'), ('Order Completed', 'Order Completed')], max_length=50),
        ),
    ]
