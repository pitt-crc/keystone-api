"""ORM for application specific database models.

Model objects are used to define the expected schema for individual database
tables and provide an object-oriented interface for executing database logic.
Each model reflects a different database and defines low-level defaults for how
the associated table/fields/records are presented by parent interfaces.
"""

from django.db import models

__all__ = ['LogEntry']


class LogEntry(models.Model):
    """A log entry"""

    time = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    pathname = models.CharField(max_length=260)
    lineno = models.IntegerField()
    message = models.TextField()
