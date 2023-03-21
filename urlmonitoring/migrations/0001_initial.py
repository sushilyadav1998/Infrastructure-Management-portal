# Generated by Django 2.2.4 on 2020-06-11 18:28

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='urlmonitoring',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ip', models.CharField(max_length=16)),
                ('username', models.CharField(max_length=15)),
                ('password', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255)),
                ('ownername', models.CharField(max_length=50)),
                ('owneremail', models.CharField(max_length=50)),
                ('ownerphno', models.CharField(max_length=10)),
            ],
        ),
    ]
