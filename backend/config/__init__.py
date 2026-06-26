"""Django project package for the SQLite MVP.

Celery is intentionally not imported here because the presentation MVP
removed the Celery dependency from requirements.txt. Importing it during
Django startup would make management commands fail before settings load.
"""

__all__ = ()
