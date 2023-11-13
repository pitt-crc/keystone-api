"""Schedule tasks executed in parallel by Celery."""

from celery import shared_task


@shared_task(name='Example Task')
def example_task():
    """This is an example"""

    print("The example task just ran.")
