"""System checks for verifying proper application configuration.

System checks are used to report configuration errors in the parent
application. See the `apps.py` file for their registration with the
Django System Checks framework.
"""

from django.core.checks import Error

import keystone_api

__all__ = ['check_celery_is_importable']


def check_celery_is_importable(app_configs, **kwargs):
    """Check the `` variable is importable from the top level package"""

    errors = []
    try:
        from keystone_api import celery_app

    except ImportError:
        errors.append(
            Error(
                "missing `celery_app` variable",
                hint="Make sure the `celery_app` variable is importable from the top level package.",
                id="apps.scheduler.E001",
                obj=keystone_api
            )
        )

    return errors
