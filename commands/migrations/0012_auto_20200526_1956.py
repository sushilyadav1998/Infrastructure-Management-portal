# Generated by Django 2.2.4 on 2020-05-26 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commands', '0011_auto_20200526_1952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storedata',
            name='swap',
            field=models.CharField(default='True', max_length=5),
        ),
    ]
