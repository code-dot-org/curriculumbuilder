# Dockerfile

# FROM directive instructing base image to build upon
FROM python:2-onbuild

ENV PYTHONUNBUFFERED 1

# EXPOSE 8000

# CMD specifies the command to execute to start the server running
# CMD ["/start.sh"]

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client python-lxml wkhtmltopdf\
    && rm -rf /var/lib/apt/lists/*

# RUN apt-get install -y --no-install-recommends python-lxml

# RUN mkdir /code
# WORKDIR /code
WORKDIR /usr/src/app/

# ADD start.sh /code/

# ADD requirements.txt /code/

RUN pip install -r requirements.txt

# ADD . /code/

# EXPOSE port 8000 to allow communication to/from server
# EXPOSE 8000

# CMD ["python", "manage.py", "runserver_plus", "0.0.0.0:8000"]
