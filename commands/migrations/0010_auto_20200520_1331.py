# Generated by Django 2.2.4 on 2020-05-20 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commands', '0009_auto_20200520_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storedata',
            name='os',
            field=models.CharField(default='True', max_length=32),
        ),
        migrations.AlterField(
            model_name='storedata',
            name='usedspace',
            field=models.CharField(default='True', max_length=3),
        ),
    ]
