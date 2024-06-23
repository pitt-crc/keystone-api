import json
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta


class BaseMocker(ABC):
    """Base class for building classes that generate random mock data"""

    _pk = 0

    def __init__(self, **kwargs):
        self.__class__._pk += 1
        self._data = self.gen_data(**kwargs)
        self._data['pk'] = self.__class__._pk

    def to_json(self) -> dict:
        """Return a JSON serializable representation of the generated data"""

        return self._data.copy()

    @abstractmethod
    def gen_data(self, **kwargs) -> dict:
        """This method must be implemented by subclasses

        This method is used to create a dictionary of random data in the desired format.
        """

        pass


class MockerEncoder(json.JSONEncoder):
    """JSON encoder for instances of the `BaseMocker` class"""

    def default(self, obj: BaseMocker) -> str | dict:
        """Return a serializable representation of a mocker instance

        Args:
            obj: The mocker object to serialize

        Returns:
            Dictionary representation of the mocked data
        """

        if isinstance(obj, BaseMocker):
            return obj.to_json()

        if isinstance(obj, (datetime, date, timedelta)):
            return str(obj)

        return super().default(obj)
