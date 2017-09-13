release: cp wkhtmltopdf/wkhtmltopdf .heroku/python/apps/
web: gunicorn --env DJANGO_SETTINGS_MODULE=curriculumBuilder.settings curriculumBuilder.wsgi --log-file -
