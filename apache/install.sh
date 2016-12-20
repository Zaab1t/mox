#!/bin/bash

DOMAIN="referencedata.dk"
while getopts "d:" OPT; do
  case $OPT in
        d)
                DOMAIN="$OPTARG"
                ;;
        *)
                echo "Usage: $0 [-d domain]"
				echo "  -d: Specify domain"
                exit 1;
                ;;
        esac
done

# Get the folder of this script
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

## System dependencies. These are the packages we need that might not be present on a fresh OS install.
if [ -z $SKIP_SYSTEM_DEPS ]; then
    echo "Installing oio_rest dependencies"
	SYSTEM_PACKAGES=$(cat "$DIR/SYSTEM_DEPENDENCIES")

	for package in "${SYSTEM_PACKAGES[@]}"; do
		sudo apt-get -y install $package
	done
fi

# Setup apache site config
CONFIGFILENAME="$DIR/mox.conf"
sed -i -e s/$\{domain\}/${DOMAIN//\//\\/}/ "$CONFIGFILENAME"
sudo ln -sf "$CONFIGFILENAME" "/etc/apache2/sites-available/mox.conf"
sudo a2ensite mox
sudo a2enmod ssl
sudo a2enmod rewrite
if [ -L /etc/apache2/sites-enabled/oio_rest.conf ]; then
	sudo a2dissite --quiet oio_rest
fi
sudo rm --force "/etc/apache2/sites-available/oio_rest.conf"

sudo service apache2 restart

