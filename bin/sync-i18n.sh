#!/bin/bash

set -e

python manage.py gather_i18n_strings
bash ./i18n/sync-up.sh
bash ./i18n/sync-down.sh
echo "i18n sync finished, content is ready to publish"
