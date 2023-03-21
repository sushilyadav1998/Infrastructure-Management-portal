# Generated by Django 2.2.4 on 2020-02-27 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='executecommand',
            fields=[
                ('ip', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=15)),
                ('password', models.CharField(max_length=255)),
                ('command', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='responsecommand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statuscode', models.CharField(default='True', max_length=8)),
                ('message', models.CharField(default='True', max_length=255)),
                ('output', models.CharField(default='True', max_length=255)),
            ],
        ),
    ]
