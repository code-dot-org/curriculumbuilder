# Curriculum Builder I18n Sync Setup

The Curriculum Builder I18n Sync runs on production daily at 7am UTC. Follow the instructions below to set up your local instance of Curriculum Builder.


### Adding API Keys

Add the following configurations to your `local_settings.py`, using the values specified in the [Heroku settings](https://dashboard.heroku.com/apps/curriculumbuilder/settings).

```
AWS_ACCESS_KEY_ID = '...'
AWS_DEFAULT_REGION = 'us-east-1'
AWS_SECRET_ACCESS_KEY = '...'
I18N_STORAGE = 'django.core.files.storage.FileSystemStorage' #this configures the sync to download translations to your local machine
JACKFROST_STORAGE = 'jackfrost.defaults.JackfrostFilesStorage'
JACKFROST_STORAGE_KWARGS = {}
CROWDIN_API_KEY='...'
```

### Running the I18n Sync

- If you want to run the full sync (this will take a while):  
```
sh bin/sync-i18n.sh
```
- If you want to run one or multiple specific steps of the i18n sync:
```
./manage.py gather_i18n_strings
./manage.py i18n_sync_up
./manage.py i18n_sync_down
./manage.py publish_i18n
```

###Testing Upload to S3

If you want to test uploading strings to S3, set the `AWS_STORAGE_BUCKET_NAME` to a test bucket in your `local_settings.py` so that you don't upload to production.
Additionally delete the `I18N_STORAGE` configuration in your `local_settings.py` so that the sync uses S3 for storage.
