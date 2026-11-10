
"""
Hamilton Temperature Analytics
October 21 - Task 13

Reusable logging configuration.

Records pipeline events without exposing
database passwords or credentials.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger():

    # Locate the project directory
    project_root = Path(__file__).resolve().parent.parent

    # Create logs folder if it doesn't exist
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Define the log file
    log_file = logs_dir / "weather_pipeline.log"

    # Create a named logger
    logger = logging.getLogger(
        "hamilton_temperature_pipeline"
    )

    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Prevent duplicate handlers
    if not logger.handlers:

        # Rotate files to limit disk usage
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=500000,
            backupCount=3,
            encoding="utf-8"
        )

        # Format each log entry
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)

    return logger


# Run this demonstration only when executed directly
if __name__ == "__main__":

    logger = get_logger()

    print("TASK 13: Python Logging Practice")

    logger.info("Logging test started.")

    logger.info("Database logging configuration ready.")

    logger.warning(
        "This is an example warning, not a real problem."
    )

    # Simulate an error safely
    try:
        raise ValueError("Intentional logging test")

    except ValueError as error:
        logger.error(
            "Test error detected: %s",
            type(error).__name__
        )

    logger.info("Logging test completed.")

    print("SUCCESS: Logging demonstration completed.")
    print("No database records were modified.")
    print("Check logs/weather_pipeline.log for entries.")
