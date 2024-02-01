"""Tests for the `LogEntrySerializer` class."""

from auditlog.models import LogEntry
from django.test import TestCase

from apps.audit.serializers import LogEntrySerializer


class RecordSerialization(TestCase):
    """Test the serialization of `LogEntry` records by the `LogEntrySerializer` class

    These tests focus on record fields for which custom serialization logic has been
    written. The serialization of other fields is trusted to the underlying framework.
    """

    def test_changes_serialization(self) -> None:
        """Test the serialization of the `changes` field"""

        log_entry_instance = LogEntry(
            id=1,
            changes="{\"field1\": [\"None\", \"abc\"], \"field2\": [\"None\", \"1\"], \"field3\": [\"True\", \"False\"]}",
        )

        expected_changes = {
            "field1": ["None", "abc"],
            "field2": ["None", "1"],
            "field3": ["True", "False"]}

        serialized_data = LogEntrySerializer(instance=log_entry_instance).data
        self.assertDictEqual(expected_changes, serialized_data['changes'])

    def test_password_is_removed(self) -> None:
        """Test the `password` field is removed from serialized list of record changes"""

        log_entry = LogEntry(**{
            'id': 1,
            'changes': "{\"field1\": [\"None\", \"abc\"], \"password\": [\"foo\", \"bar\"]}",
        })

        serialized_data = LogEntrySerializer(instance=log_entry).data
        self.assertNotIn('password', serialized_data['changes'])
