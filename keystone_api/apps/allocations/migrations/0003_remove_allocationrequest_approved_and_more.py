# Generated by Django 4.2.11 on 2024-03-25 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('allocations', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='allocationrequest',
            name='approved',
        ),
        migrations.RemoveField(
            model_name='allocationrequestreview',
            name='approve',
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='status',
            field=models.CharField(choices=[('PD', 'Pending'), ('AP', 'Approved'), ('DC', 'Declined'), ('CR', 'Changes Requested')], default='PD', max_length=2, verbose_name='Review Status'),
        ),
        migrations.AddField(
            model_name='allocationrequestreview',
            name='status',
            field=models.CharField(choices=[('AP', 'Approved'), ('DC', 'Declined'), ('CR', 'Changes Requested')], default='PD', max_length=2),
            preserve_default=False,
        ),
    ]
