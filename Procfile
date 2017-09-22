release: python manage.py createinitialrevisions
web: bin/start-pgbouncer-stunnel newrelic-admin run-program waitress-serve --port=$PORT --send-bytes=1 curriculumBuilder.wsgi:application
