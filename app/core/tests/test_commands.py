"""Test custom django management commands."""

from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch("core.management.commands.wait_for_db.Command.check")
class CommandTest(SimpleTestCase):
    """Test command"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for db to be ready"""
        # Simulate database ready on first check
        patched_check.return_value = True

        # Run the wait_for_db command
        call_command("wait_for_db")

        # Ensure it was called once
        patched_check.assert_called_once_with(databases=["default"])

    @patch("time.sleep")
    def test_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError"""
        # Simulate 2 Psycopg2 errors, 3 OperationalErrors, then successful connection
        patched_check.side_effect = (
            [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]
        )

        # Run the wait_for_db command
        call_command("wait_for_db")

        # Assert check was called 6 times
        self.assertEqual(patched_check.call_count, 6)

        # Assert last call was with databases=['default']
        patched_check.assert_called_with(databases=["default"])

# Ensure a blank line at the end of the file