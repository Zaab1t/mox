#!/bin/bash -e
set -b

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

cd $DIR
source ./config.sh

read -r -p \
     "You are about to destroy ALL DATA in your current database. Proceed? [y/N] " \
     input

case $input in
    [yY][eE][sS]|[yY])
		# do nothing
		;;

    *)
	exit 1
	;;
esac

export PGPASSWORD="$MOX_DB_PASSWORD"
# TODO: Support remote Postgres DB server
#export PGHOST="$MOX_DB_HOST"

sudo -u postgres dropdb --if-exists $MOX_DB
sudo -u postgres dropuser --if-exists $MOX_DB_USER

exec $DIR/initdb.sh
