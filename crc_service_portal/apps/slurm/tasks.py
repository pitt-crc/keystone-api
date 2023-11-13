from celery import shared_task


@shared_task(name='Example Task')
def example_task():
    print("The example task just ran.")
