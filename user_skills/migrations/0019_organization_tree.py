# Generated by Django 5.1.4 on 2025-01-28 11:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_skills', '0018_remove_certificateusermap_unique_user_certificate_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization_tree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('empname', models.CharField(max_length=200)),
                ('mgrid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_skills.organization_tree')),
            ],
        ),
    ]
