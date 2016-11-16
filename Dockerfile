FROM ubuntu:14.04
MAINTAINER Dan Villiom Podlaski Christiansen <dan@magenta.dk>

# initial config
ENV DEBIAN_FRONTEND=noninteractive
ENV deps="python python-setuptools libxmlsec1-openssl postgresql-client ca-certificates"
ENV build_deps="python-pip libxmlsec1-dev devscripts equivs"
ENV source_packages="psycopg2 m2crypto"

# ensure the box is up-to-date
RUN apt-get -qqy update
RUN apt-get -qqy dist-upgrade

# now install the basic dependancies
RUN apt-get -qqy install --no-install-recommends \
            $deps $build_deps

# the source_packages are python modules with a lot of build
# dependencies. we install the dependencies using mk-build-deps, and
# mark the generated package as automatically installed -- this way,
# we can easily uninstall it all later
RUN cd /tmp; \
    for pkg in $source_packages; do \
      mk-build-deps -irt 'apt-get -qy' $pkg; \
      apt-mark markauto $pkg-build-deps; \
    done

# copy the python sources into place -- we do this early so changes to
# the Dockerfile doesn't invalidate build images
COPY oio_rest /srv/mox/oio_rest

# now build & install all our python dependancies
RUN python /srv/mox/oio_rest/setup.py develop

# install gunicorn for serving the WSGI app
RUN pip -q install gunicorn gevent setproctitle

# cleanup
# FIXME: pointless? it appears we shrink the footprint...
RUN apt-get -qy purge --auto-remove $build_deps

# copy the rest of the sources into place
COPY . /srv/mox

# add a 'mox' user
RUN useradd --home-dir /srv/mox mox
RUN install -d -o mox -g mox /var/log/oio_rest /var/run/oio_rest

# gunicorn takes the wsgi script as an importable python module
RUN ln -s server-setup/oio_rest.wsgi /srv/mox/oio_rest/oio_wsgi.py

# runtime config for gunicorn
WORKDIR /srv/mox/oio_rest
CMD [ "/usr/local/bin/gunicorn", \
      "-c", "server-setup/gunicorn-config.py", "oio_wsgi" ]

EXPOSE 8000
