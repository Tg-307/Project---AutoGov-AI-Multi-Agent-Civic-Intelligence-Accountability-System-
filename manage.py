#!/usr/bin/env python
import os
import sys


def check_deps():
    missing = []
    for pkg in ['django', 'rest_framework']:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print("="*50)
        print("MISSING PACKAGES — run:  pip install -r requirements.txt")
        print("Missing:", ", ".join(missing))
        print("="*50)
        sys.exit(1)


def main():
    check_deps()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autogov.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
