#!/usr/bin/env python3
"""
Module for filtering and redacting personal information in log messages.

This module provides functionality for connecting to a MySQL database, 
retrieving user data, and logging it while redacting sensitive information.
The redaction is done using regular expressions to ensure that personal 
information is not exposed in log files.

Auteur SAID LAMGHARI
"""

import re
from typing import List
import logging
import mysql.connector
import os


class RedactingFormatter(logging.Formatter):
    """
    Custom logging formatter that redacts sensitive information in log messages.

    This formatter uses a specified list of fields and replaces their values 
    with a redaction string (e.g., '***') to prevent exposing sensitive data.

    Attributes:
        REDACTION (str): The string used to replace sensitive data in log messages.
        FORMAT (str): The format string for log messages.
        SEPARATOR (str): The character used to separate fields in the log message.
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]) -> None:
        """
        Initialize the RedactingFormatter with fields to be redacted.

        Args:
            fields (List[str]): A list of field names that need to be redacted.
        """
        super().__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record, redacting specified fields.

        This method overrides the base format method to apply redaction to the 
        log message before formatting it.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message with sensitive data redacted.
        """
        # Call the base class format method to get the formatted log message
        frmttd_mssge = super().format(record)
        # Apply redaction to the formatted log message
        return filter_datum(self.fields,
                            self.REDACTION, frmttd_mssge, self.SEPARATOR)


PII_FIELDS = ("name", "email", "password", "ssn", "phone")
"""
List of fields that should be redacted from log messages.
These fields are considered personally
identifiable information (PII).
"""


def get_db() -> mysql.connector.connection.MYSQLConnection:
    """
    Establish a connection to the MySQL database using environment variables.

    Returns:
        mysql.connector.connection.MYSQLConnection:
            The database connection object.

    Raises:
        mysql.connector.Error: If there is an error connecting to the database.
    """
    getdb_var = mysql.connector.connect(
        user=os.getenv('PERSONAL_DATA_DB_USERNAME', 'root'),
        password=os.getenv('PERSONAL_DATA_DB_PASSWORD', ''),
        host=os.getenv('PERSONAL_DATA_DB_HOST', 'localhost'),
        database=os.getenv('PERSONAL_DATA_DB_NAME')
    )
    return getdb_var


def filter_datum(fields: List[str], redaction: str, message: str, separator: str) -> str:
    """
    Redact specified fields in the log message using a single regex pattern.

    This function constructs a regex pattern to match fields that need to be 
    redacted and uses re.sub to replace their values with the redaction string.

    Args:
        fields (List[str]): A list of field names to redact.
        redaction (str): The string used to replace sensitive data.
        message (str): The log message to filter.
        separator (str): The separator used to delimit fields in the message.

    Returns:
        str: The filtered log message with redacted fields.
    """
    # Create a regex pattern that matches any of the specified fields
    pattern = '|'.join([f'{field}=[^;]*{separator}' for field in fields])
    # Replace matched fields with redacted value
    return re.sub(pattern, lambda m: f'{m.group(0).split("=")[0]}={redaction}{separator}', message)


def get_logger() -> logging.Logger:
    """
    Create and configure a logger that uses the RedactingFormatter.

    This function sets up a logger with a stream handler and applies the 
    custom RedactingFormatter to ensure sensitive information is redacted 
    in log messages.

    Returns:
        logging.Logger: The configured logger instance.
    """
    lgger_dt = logging.getLogger("user_data")
    lgger_dt.setLevel(logging.INFO)
    lgger_dt.propagate = False

    trgt_hndlr = logging.StreamHandler()
    trgt_hndlr.setLevel(logging.INFO)

    # Instantiate the custom formatter with the list of PII fields
    formatter = RedactingFormatter(list(PII_FIELDS))
    trgt_hndlr.setFormatter(formatter)

    lgger_dt.addHandler(trgt_hndlr)
    return lgger_dt


def main() -> None:
    """
    Main function to retrieve and log user data from
    the database, redacting sensitive information.

    This function connects to the database, retrieves all rows from the 'users' table,
    and logs each row with sensitive fields redacted.
    """
    # Establish database connection
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")

    # Retrieve column headers from the cursor description
    headers = [field[0] for field in cursor.description]
    logger = get_logger()

    # Iterate over each row in the result set
    for rw in cursor:
        infodata = ''
        # Construct the log message by combining field names and values
        for f, p in zip(rw, headers):
            infodata += f'{p}={f}; '
        # Log the constructed message
        logger.info(infodata.strip())  # Strip trailing space

    # Close database resources
    cursor.close()
    db.close()


if __name__ == '__main__':
    # Run the main function when the script is executed directly
    main()
