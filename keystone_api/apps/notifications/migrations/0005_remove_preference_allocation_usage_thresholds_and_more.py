# Generated by Django 5.0.8 on 2024-09-01 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_rename_alloc_thresholds_preference_allocation_usage_thresholds_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preference',
            name='allocation_usage_thresholds',
        ),
        migrations.RemoveField(
            model_name='preference',
            name='notify_status_update',
        ),
        migrations.AddField(
            model_name='preference',
            name='notify_on_expiration',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('GM', 'General Message'), ('RE', 'Request Expiring Notice'), ('RD', 'Request Expired Notice')], default='GM', max_length=2),
        ),
    ]