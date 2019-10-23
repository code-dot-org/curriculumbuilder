#!/bin/bash

# Try to run the four steps of the i18n sync in sequence and then log a success
# message. If any of the four steps (or the process of logging the success
# message) fail, log an error message.
python manage.py gather_i18n_strings && \
  python manage.py i18n_sync_up && \
  python manage.py i18n_sync_down && \
  python manage.py publish_i18n && \
  python manage.py log_i18n_success || \
  python manage.py log_i18n_failure
