#!/bin/bash

# Start Gunicorn Process
echo Starting Gunicorn
exec gunicorn curriculumbuilder.wsgi:application --bind 0.0.0.0:8000 --workers 3
