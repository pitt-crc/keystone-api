"""Schedule tasks executed in parallel by Celery."""

from celery import shared_task


@shared_task(name='Update Account Status')
def update_account_status():
    """Lock/unlock user accounts based on the status of their SU allocation"""
