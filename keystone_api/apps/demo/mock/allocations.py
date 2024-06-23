import random
from datetime import timedelta
from tempfile import NamedTemporaryFile

from faker import Faker

from apps.demo.mock.base import BaseMocker

faker = Faker()


class ClusterMocker(BaseMocker):
    def gen_data(self, **kwargs) -> dict:
        kwargs.setdefault('name', faker.word(part_of_speech='noun').title())
        kwargs.setdefault('description', faker.text(max_nb_chars=150))
        kwargs.setdefault('enabled', random.choice([True, False]))
        return kwargs


class AllocationRequestMocker(BaseMocker):
    def gen_data(self, **kwargs) -> dict:
        kwargs.setdefault('title', faker.catch_phrase().title())
        kwargs.setdefault('description', faker.text(max_nb_chars=1600))
        kwargs.setdefault('submitted', faker.date_this_year())
        kwargs.setdefault('status', random.choice(['PD', 'AP', 'DC', 'CR']))
        kwargs['pk'] = BaseMocker._pk  # Assigning pk from BaseMocker
        BaseMocker._pk += 1  # Incrementing pk for the next instance

        if kwargs['status'] == 'AP':
            active = faker.date_between(start_date=kwargs['submitted'], end_date='+30d')
            expire = active + timedelta(days=30) if active else None
        else:
            active = None
            expire = None

        kwargs.setdefault('active', active)
        kwargs.setdefault('expire', expire)

        return kwargs


class AttachmentMocker(BaseMocker):
    def gen_data(self, **kwargs) -> dict:
        kwargs.setdefault('uploaded', faker.date_time_this_year())
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b'This is some test file data.')
            temp_file.seek(0)
            kwargs.setdefault('file_data', temp_file)

        return kwargs


class AllocationRequestReviewMocker(BaseMocker):
    def gen_data(self, **kwargs) -> dict:
        kwargs.setdefault('status', random.choice(['AP', 'DC', 'CR']))
        kwargs.setdefault('date_modified', faker.date_time_this_year())

        if random.choice([True, False]):
            kwargs.setdefault('public_comments', faker.text(max_nb_chars=1600))

        if random.choice([True, False]):
            kwargs.setdefault('private_comments', faker.text(max_nb_chars=1600))

        return kwargs


class AllocationMocker(BaseMocker):
    def gen_data(self, **kwargs) -> dict:
        kwargs.setdefault('requested', faker.random_int(min=10_000, max=1_000_000, step=10_000))

        if random.choice([True, False]):
            kwargs.setdefault('awarded', faker.random_int(min=0, max=kwargs['requested'], step=5_000))

        if kwargs.get('awarded', False) and random.choice([True, False]):
            kwargs.setdefault('final', faker.random_int(min=0, max=kwargs['awarded'], step=1000))

        return kwargs
