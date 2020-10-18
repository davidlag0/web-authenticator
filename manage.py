#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webtools.settings')
    try:
        # pylint: disable=import-outside-toplevel
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Code coverage is handled here because of a bug with Django and nose that
    # hasn't been fixed after years.
    is_testing = 'test' in sys.argv[1]

    if is_testing:
        # pylint: disable=import-outside-toplevel
        from coverage import Coverage
        cov = Coverage()
        cov.erase()
        cov.start()

    execute_from_command_line(sys.argv)

    if is_testing:
        cov.stop()
        cov.save()
        cov.report()
        cov.html_report(directory='htmlcov')
        cov.xml_report()


if __name__ == '__main__':
    main()
