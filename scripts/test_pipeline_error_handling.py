
"""
Hamilton Temperature Analytics
October 21 - Task 15

Test weather pipeline error handling.

All API calls and database connections
are mocked during these tests.

No actual database records are modified.
"""

import runpy
from io import StringIO
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

import requests


# Locate the working pipeline

PIPELINE_PATH = (
    Path(__file__).resolve().parent
    / "weather_pipeline.py"
)


def test_failure(
    test_name,
    expected_error,
    api_error=None,
    api_response=None
):
    """
    Run the real pipeline's error handler
    using simulated API behavior.

    Real network calls and database
    connections are disabled.
    """

    print("\n" + "=" * 45)
    print(test_name)
    print("=" * 45)

    with patch("requests.get") as mock_request, \
         patch("psycopg.connect") as mock_database:

        # Configure the simulated API behavior

        if api_error is not None:
            mock_request.side_effect = api_error

        else:
            mock_request.return_value = api_response

        # Capture terminal output

        captured = StringIO()

        try:
            with redirect_stdout(captured):

                runpy.run_path(
                    str(PIPELINE_PATH),
                    run_name="__main__"
                )

        except SystemExit as error:

            # The pipeline should stop with
            # a nonzero exit code on failure.

            if error.code != 1:
                raise AssertionError(
                    "Unexpected pipeline exit code."
                )

        else:
            raise AssertionError(
                "Pipeline did not report the failure."
            )

        # Check that the appropriate error
        # message appeared in terminal output.

        output = captured.getvalue()

        expected_message = (
            "ERROR: Pipeline failed: "
            + expected_error
        )

        if expected_message not in output:
            raise AssertionError(
                "Expected error was not reported.\n"
                + output
            )

        # No real or mocked database connection
        # should have been attempted.

        mock_database.assert_not_called()

        print("Expected error:", expected_error)
        print("SUCCESS: Error was detected.")
        print("SUCCESS: Pipeline stopped safely.")
        print("SUCCESS: No database connection attempted.")


def main():

    print("TASK 15: Pipeline Error Handling Tests")

    # TEST 1: Simulate an API timeout
    # 

    test_failure(
        test_name="TEST 1: API TIMEOUT",
        expected_error="Timeout",
        api_error=requests.exceptions.Timeout(
            "Simulated API timeout"
        )
    )

    
    # TEST 2: Simulate incomplete API data

    incomplete_response = Mock()

    incomplete_response.json.return_value = {
        "hourly": {
            "time": [
                "2025-01-01T00:00"
            ],
            "temperature_2m": [
                2.2
            ]
        }
    }

    test_failure(
        test_name="TEST 2: INCOMPLETE API DATA",
        expected_error="ValueError",
        api_response=incomplete_response
    )

    
    # TEST 3: Simulate malformed API response

    malformed_response = Mock()

    malformed_response.json.return_value = {
        "hourly": {
            "unexpected_field": []
        }
    }

    test_failure(
        test_name="TEST 3: MALFORMED API RESPONSE",
        expected_error="KeyError",
        api_response=malformed_response
    )

    print("\n" + "=" * 45)
    print("SUCCESS: ALL TASK 15 TESTS PASSED!")
    print("All simulated failures were handled.")
    print("No database connections were attempted.")


if __name__ == "__main__":

    main()
