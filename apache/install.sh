#!/bin/bash -e

# Get the folder of this script
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

## System dependencies. These are the packages we need that might not be present on a fresh OS install.
if [ -z $SKIP_SYSTEM_DEPS ]; then
    echo "Installing oio_rest dependencies"
	sudo apt-get -qy install $(cat "$DIR/SYSTEM_DEPENDENCIES")
fi

# Setup apache site config
CONFIGFILENAME="mox.conf"
sed --in-place --expression="s|\${domain}|${DOMAIN}|" "$DIR/$CONFIGFILENAME"
sudo ln --symbolic --force "$DIR/$CONFIGFILENAME" "/etc/apache2/sites-available/$CONFIGFILENAME"
sudo a2dissite 000-default.conf
sudo a2ensite mox
sudo a2enmod ssl
sudo a2enmod rewrite
if [ -L /etc/apache2/sites-enabled/oio_rest.conf ]; then
	sudo a2dissite --quiet oio_rest
fi
if [ -f /etc/apache2/sites-enabled/oio_rest.conf ]; then
	sudo rm --force "/etc/apache2/sites-available/oio_rest.conf"
fi

sudo service apache2 restart

