#!/usr/bin/env python
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Point to the correct settings location inside app/app/
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "app.settings"
    )  # This assumes settings.py is in the app/app folder

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        try:
            import django
            from django.core.management import execute_from_command_line
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable?"
            )
    execute_from_command_line(sys.argv)


"""Django's command-line utility for administrative tasks."""
'''import os
import sys


def main():
    """Run administrative tasks."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.app.settings")


    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()'''
