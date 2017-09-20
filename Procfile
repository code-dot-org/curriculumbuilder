release: python manage.py createinitialrevisions
web: waitress-serve --port=$PORT --send-bytes=1 curriculumBuilder.wsgi:application
