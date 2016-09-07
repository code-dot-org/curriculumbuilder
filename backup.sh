#!/bin/bash
# Backs up the OpenShift PostgreSQL database for this application
# by Skye Book
NOW="$(date +"%Y-%m-%d")"
FILENAME="$OPENSHIFT_DATA_DIR/$OPENSHIFT_APP_NAME.$NOW.backup.sql.gz"
pg_dump $OPENSHIFT_APP_NAME -h $OPENSHIFT_POSTGRESQL_DB_HOST | gzip > $FILENAME