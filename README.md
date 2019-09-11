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

5. work around pycurl installation problem (https://cscheng.info/2018/01/26/installing-pycurl-on-macos-high-sierra.html)
```
export PYCURL_SSL_LIBRARY=openssl
export LDFLAGS="-L/usr/local/opt/openssl/lib" 
export CPPFLAGS="-I/usr/local/opt/openssl/include"
```
to avoid future problems, also set these variables in your ~/.bashrc file.

6. install python dependencies
```
pip install -r requirements.txt
```
if you are returning to this step to fix problems with pycurl, you may need to also add the `--no-cache-dir` flag.

7. copy the db

```
heroku login # need credentials from Josh C.
heroku pg:pull DATABASE_URL curriculumbuilder -a curriculumbuilder
```

8. set up local_settings.py

```
cp curriculumBuilder/local_settings.py.example curriculumBuilder/local_settings.py
```

9. run the tests

```
npm install
./manage.py test
```

10. run the server

```
source ~/.virtualenvs/cb/bin/activate # must be run once per shell window
debug=true python manage.py runserver_plus
```

http://localhost:8000

12. In order to create PRs 

```
Make sure to ask JoshC to add you as an contributor to the repo
```

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
