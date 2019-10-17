Code.org CurriculumBuilder
=
An internal tool designed for Code.org curricula

### How to use CurriculumBuilder
- Go to the #curriculumbuilder-dev channel for support

### How to install Curriculum Builder locally on OS X

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
if you are returning to this step to fix problems with pycurl, you may need to also add the `--no-cache-dir` flag.

6. copy the db

```
heroku login # need credentials from Josh C.
heroku pg:pull DATABASE_URL curriculumbuilder -a curriculumbuilder
```

7. set up local_settings.py

```
cp curriculumBuilder/local_settings.py.example curriculumBuilder/local_settings.py
```

8. run the tests

```
npm install
./manage.py test
```

9. run the server

```
source ~/.virtualenvs/cb/bin/activate # must be run once per shell window
debug=true python manage.py runserver_plus
```

http://localhost:8000

10. troubleshooting pycurl

    There are two potential errors you can get which look very similar:

  * `ImportError: pycurl: libcurl link-time ssl backend (openssl) is different from compile-time ssl backend (none/other)`
    
    solution: https://cscheng.info/2018/01/26/installing-pycurl-on-macos-high-sierra.html

  * `ImportError: pycurl: libcurl link-time ssl backend (none/other) is different from compile-time ssl backend (openssl)`
  
    solution: https://gist.github.com/webinista/b4b6a4cf8f158431b2c5134630c2cbfe#gistcomment-3057612

11. measure test coverage
```
pip install -r requirements-dev.txt
DJANGO_SETTINGS_MODULE=curriculumBuilder.settings debug=true coverage run ./manage.py test
coverage report
```
If you run this often, it may be worth appending the `--keepdb` flag to make it run faster, 
and temporarily disabling any tests which fail as a result.

### How does the deploy work on CurriculumBuilder

CurriculumBuilder is actually two separate websites:
* [codecurricula.com](codecurricula.com) - where curriculum writers edit the curriculum
* [curriculum.code.org](curriculum.code.org) - where teachers access the curriculum

When you add a feature to CurriculumBuilder by merging a commit your
change will automatically be deployed to [codecurricula.com](codecurricula.com).
You can watch the #curriculumbuilder channel to see when it gets deployed.

In order for your change to show up on [curriculum.code.org](curriculum.code.org)
all of the impacted curriculum must be republished. Developers should ask
the curriculum team to republish their curriculum so that we don't accidentally
ship a change to the curriculum that was not ready to go out.

### Updating your local database schema

To update your local database schema use the following command:
```
./manage.py migrate
```

### Updating your local database contents

```
dropdb curriculumbuilder
heroku pg:pull DATABASE_URL curriculumbuilder -a curriculumbuilder
```

### Creating a new user

If you have an account and are a superuser, you can create new CurriculumBuilder users by doing the following:

1. Log in at [codecurricula.com/admin](codecurricula.com/admin). Choose the "admin" interface.
2. Choose the "Users" option in the left-hand navigation menu, or go to [codecurricula.com/admin/auth/user/](codecurricula.com/admin/auth/user/). Here, you can view, update, and create users.
3. Use the "Add user" button to create a new user.
4. Set the user's permissions:
  * All users need to have `www.codecurricula.com` added to their site permissions.
  * All staff members will need "staff status" set to true.
  * Curriculum writers need to be added to the "author" group.
5. If you need this new user for local development purposes, [update your local database contents](https://github.com/mrjoshida/curriculumbuilder#updating-your-local-database-contents).
