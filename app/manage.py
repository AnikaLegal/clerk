#!/usr/bin/python3
import os
import sys
from django.conf import settings

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clerk.settings")

    attach_debugger = settings.DEBUG and (
        os.environ.get("RUN_MAIN") or os.environ.get("WERKZEUG_RUN_MAIN")
    )
    if attach_debugger:
        import debugpy

        debugpy.listen(("0.0.0.0", 8123))
        print("VSCode debugger attached.")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
