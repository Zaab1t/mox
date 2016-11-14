FROM python:2.7-onbuild

COPY "server-setup/oio_rest.wsgi" "oio_wsgi.py"

# get a few packages from debian that are quite annoying to build
RUN apt-get -qqy update
RUN apt-get -qqy install apt-utils libxmlsec1-dev python-m2crypto python-lxml

RUN pip install Flask Jinja2 psycopg2 pexpect python-saml gunicorn enum34

# RUN "python" "setup.py" "develop"

CMD [ "/usr/local/bin/gunicorn", "--env", "NO_VENV=1", "oio_wsgi" ]
EXPOSE 8000
