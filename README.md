Code.org CurriculumBuilder
=
An internal tool designed for Code.org curricula

### How to use CurriculumBuilder
- For now, ask josh...

### How to install Curriculum Builder locally on OS X

You'll probably end up asking josh anyway, but why not try this first...

1. install mac os x dependencies

  ```
  brew install openssl postgres heroku/brew/heroku Caskroom/cask/wkhtmltopdf
  brew services start postgresql
  ```

2. make sure you have python 2.7

  ```
  python -V # -> Python 2.7.10
  ```
  if you don't, try installing it:
  ```
  brew install python@2
  ```
  And then run `python -V` again to make sure you now have version 2.7 installed. If you don't, stop here and try to get yourself onto this version of python before proceeding.

3. clone repo

```
git clone https://github.com/mrjoshida/curriculumbuilder.git
cd curriculumbuilder
```

4. set up virtualenv (https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv)

```
pip install virtualenv
mkdir ~/.virtualenvs
virtualenv ~/.virtualenvs/cb
source ~/.virtualenvs/cb/bin/activate
```

5. install python dependencies

```
pip install -r requirements.txt
```

6. work around pycurl problem (https://cscheng.info/2018/01/26/installing-pycurl-on-macos-high-sierra.html)

```
export PYCURL_SSL_LIBRARY=openssl
pip uninstall pycurl
pip install --install-option="--with-openssl" --install-option="--openssl-dir=/usr/local/opt/openssl" pycurl
```

7. copy the db

```
heroku login # need credentials from Josh C.
heroku pg:pull DATABASE_URL curriculumbuilder -a curriculumbuilder
```

8. Set up local_setting.py

```
create curruculumbuilder/curriculumBuilder/local_settings.py
Put the following in the file:
import os
import sys

PROJECT_APP_PATH = os.path.dirname(os.path.abspath(__file__))
#PROJECT_APP = os.path.basename(PROJECT_APP_PATH)
PROJECT_ROOT = BASE_DIR = os.path.dirname(PROJECT_APP_PATH)

DEBUG = True

sys.dont_write_bytecode = True

SLACK_BACKEND = 'django_slack.backends.DisabledBackend'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
#DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
COMPRESS_STORAGE = 'compressor.storage.CompressorFileStorage'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

9. run the server

```
source ~/.virtualenvs/cb/bin/activate # must be run once per shell window
python manage.py runserver_plus
```

http://localhost:8000
