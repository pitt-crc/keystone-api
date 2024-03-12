import logging
from logging import Handler


class DBHandler(Handler):
    """Logging handler for storing log records in the application database"""

    def __init__(self, level: int = logging.NOTSET) -> None:
        """Configure the log handler

        Args:
            level: Only save log records with a logging levl abv this value
        """

        super().__init__(level=level)

    def emit(self, record: logging.LogRecord) -> None:
        """Record a log record to the database

        Args:
            record: The log record to save
        """

        # Models cannot be imported until Django has loaded the app registry
        from .models import LogEntry

        if record.levelno > self.level:
            LogEntry(
                level=record.levelname,
                name=record.name,
                pathname=record.pathname,
                lineno=record.lineno,
                message=self.format(record)
            ).save()
