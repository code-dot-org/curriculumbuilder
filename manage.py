#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    from mezzanine.utils.conf import real_project_name

    settings_module = "%s.settings" % real_project_name("curriculumBuilder")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    from django.core.management import execute_from_command_line
    from django.utils.log import getLogger

    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        logger = getLogger('management_commands')
        logger.error('Management Command Error: %s', ' '.join(sys.argv), exc_info=sys.exc_info())
        raise e
