#!/bin/bash

set -e

python manage.py gather_i18n_strings
python manage.py i18n_sync_up
python manage.py i18n_sync_down
echo "i18n sync finished, content is ready to publish"
