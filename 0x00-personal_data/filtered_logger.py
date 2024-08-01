#!/usr/bin/env python3
"""
Module fr handling personal
data with secure logging.
Autor : SAID LAMGHARI
"""

import mysql.connector
import os
import re
import logging
from typing import List, Tuple


def filter_datum(fields: List[str],
                 redaction: str, message: str,
                 separator: str) -> str:
    """
    Obfuscates sensitive fields in a log message.

    Args:
        fields (List[str]): The list of fields to obfuscate.
        redaction (str): The string to replace the field value with.
        message (str): The original log message.
        separator (str): The character separating fields in the message.

    Returns:
        str: The obfuscated log message.
    """
    pattern = f"({'|'.join(fields)})=.*?({separator}|$)"
    return re.sub(pattern,
                  lambda m: f"{m.group(1)}={redaction}{separator}", message)


class RedactingFormatter(logging.Formatter):
    """
    Formatter for logging with
    redaction of sensitive fields.
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """
        Initializes the formatter with the specified fields to redact.

        Args:
            fields (List[str]): The list of fields to redact.
        """
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Redacts sensitive fields in the log record message.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted and redacted log message.
        """
        record.msg = filter_datum(self.fields,
                                  self.REDACTION,
                                  record.getMessage(),
                                  self.SEPARATOR)
        return super().format(record)


PII_FIELDS: Tuple[str, ...] = ("name", "email", "phone", "ssn", "password")


def get_logger() -> logging.Logger:
    """
    Configures and returns a logger for user data with redaction.

    Returns:
        logging.Logger: The configured logger.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.addHandler(handler)
    return logger



def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Ctest
    """
    coctor = mysql.connector.connect(
        host=os.getenv('PERSONAL_DATA_DB_HOST'),
        database=os.getenv('PERSONAL_DATA_DB_NAME'),
        user=os.getenv('PERSONAL_DATA_DB_USERNAME'),
        password=os.getenv('PERSONAL_DATA_DB_PASSWORD')
    )
    return coctor
