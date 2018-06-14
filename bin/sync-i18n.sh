#!/bin/bash

set -e

python manage.py gather_i18n_strings
python manage.py i18n_sync_up
python manage.py i18n_sync_down
python manage.py publish_i18n
