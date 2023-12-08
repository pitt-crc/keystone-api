"""Serializers for casting database models to/from JSON and XML representations.

Serializers handle the casting of database models to/from HTTP compatible
representations in a manner that is suitable for use by RESTful endpoints.
They encapsulate object serialization, data validation, and database object
creation.
"""

from auditlog.models import LogEntry
from rest_framework import serializers

__all__ = ['LogEntrySerializer']


class LogEntrySerializer(serializers.ModelSerializer):
    """Object serializer for the `Publication` class"""

    class Meta:
        """Serializer settings"""

        model = LogEntry
        fields = '__all__'
