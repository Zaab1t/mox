#!/bin/bash -e

# TODO: bail if root
if [ `id -u` == 0 ]; then
	echo "Do not run as root. We'll sudo when necessary"
	exit 1;
fi

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Query for hostname
DOMAIN=$(hostname --fqdn)

read -p "Host name: [$DOMAIN] " -r
echo
if [[ "x$REPLY" != "x" ]]; then
	DOMAIN="$REPLY"
fi

read -p "Install WSO2 identity provider? [N/y] " -r -n 1
echo
if [[ $REPLY != [yY] ]]
then
	USE_WSO2=false
else
	USE_WSO2=true
fi

AMQP_HOST="$DOMAIN"
AMQP_USER="guest"
AMQP_PASS="guest"

REST_HOST="https://$DOMAIN"
REST_USER="admin"
REST_PASS="admin"

# Add system user if none exists
if ! getent passwd mox > /dev/null
then
	echo "Creating system user 'mox'"
	sudo useradd mox
fi

# Create log dir
echo "Creating log dir"
sudo mkdir -p "/var/log/mox"

# Config files that may be altered during install should be copied from git, but not themselves be present there
MOX_CONFIG="$DIR/mox.conf"
cp --remove-destination "$MOX_CONFIG.base" "$MOX_CONFIG"

SHELL_CONFIG="$DIR/variables.sh"
cp --remove-destination "$SHELL_CONFIG.base" "$SHELL_CONFIG"

OIO_REST_CONFIG="$DIR/oio_rest/oio_rest/settings.py"
cp --remove-destination "$OIO_REST_CONFIG.base" "$OIO_REST_CONFIG"
sed -i -e s/$\{domain\}/${DOMAIN//\//\\/}/ "$OIO_REST_CONFIG"

APACHE_CONFIG="$DIR/apache/mox.conf"
cp --remove-destination "$APACHE_CONFIG.base" "$APACHE_CONFIG"

# Setup common config
sed -i -e s/$\{domain\}/${DOMAIN//\//\\/}/ "$MOX_CONFIG"

# Setup apache virtualhost
echo "Setting up Apache virtualhost"
$DIR/apache/install.sh

if $USE_WSO2
then
	echo "Setting up Identity Server"
	$DIR/wso2/install.sh "$DOMAIN"
fi

REINSTALL_VIRTUALENVS=""
read -p "Reinstall python virtual environments [(y)es/(n)o/(A)sk every time] " -r -n 1
echo
if [[ $REPLY == [yY] ]]; then
	REINSTALL_VIRTUALENVS="--overwrite-virtualenv"
elif [[ $REPLY == [nN] ]]; then
	REINSTALL_VIRTUALENVS="--keep-virtualenv"
fi

# Install oio_rest
echo "Installing oio_rest"
echo "$DIR/oio_rest/install.py $REINSTALL_VIRTUALENVS"
$DIR/oio_rest/install.py $REINSTALL_VIRTUALENVS

# Install database
echo "Installing database"
echo "$DIR/db/install.sh"
$DIR/db/install.sh


JAVA_HIGHEST_VERSION=0
JAVA_VERSION_NEEDED=8
JAVA_HIGHEST_VERSION_DIR=""
regex=".*/java-([0-9]+).*"
files=`find /usr/lib -wholename '*/bin/javac' -perm -a=x -type f`
for f in $files; do
	if [[ $f =~ $regex ]]; then
		version="${BASH_REMATCH[1]}"
		if [[ $version > $JAVA_HIGHEST_VERSION ]]; then
			JAVA_HIGHEST_VERSION=$version
			JAVA_HIGHEST_VERSION_DIR=$(readlink -m "$f/../..")
		fi
    fi
done
if [ $JAVA_HIGHEST_VERSION -ge $JAVA_VERSION_NEEDED ]; then
	echo "Java is installed in version $JAVA_HIGHEST_VERSION"
else
	echo "Installing java in version $JAVA_VERSION_NEEDED"
	if ! apt-cache show "openjdk-$JAVA_VERSION_NEEDED-jdk" > /dev/null 2>&1
	then
		# openjdk is not available in the version we want
		sudo apt-get -qqy install software-properties-common
		sudo add-apt-repository -ys ppa:openjdk-r/ppa
		sudo apt-get -qq update
	fi
	sudo apt-get --yes --quiet install "openjdk-$JAVA_VERSION_NEEDED-jdk"
	JAVA_HIGHEST_VERSION_DIR="/usr/lib/jvm/java-$JAVA_VERSION_NEEDED-openjdk-amd64"
fi
if [[ "x$JAVA_HIGHEST_VERSION_DIR" != "x" ]]; then
	sed -r -e "s|^CMD_JAVA=.*$|CMD_JAVA=$JAVA_HIGHEST_VERSION_DIR/bin/java|" \
       -e "s|^CMD_JAVAC=.*$|CMD_JAVAC=$JAVA_HIGHEST_VERSION_DIR/bin/javac|" \
       ${SHELL_CONFIG} > ${SHELL_CONFIG}.$$
fi
if [[ -f ${SHELL_CONFIG}.$$ ]]; then
	/bin/mv ${SHELL_CONFIG}.$$ ${SHELL_CONFIG}
fi

OLD_JAVA_HOME="$JAVA_HOME"
JAVA_HOME="$JAVA_HIGHEST_VERSION_DIR"
export JAVA_HOME

# Install Maven
echo "Installing Maven"
sudo apt-get -y install maven

# Compile modules
echo "Installing java modules"
$DIR/agentbase/java/install.sh

echo "$DIR/agentbase/python/mox" > "$DIR/agentbase/python/mox/mox.pth"

# Compile agents
echo "Installing Agents"
$DIR/agents/MoxTabel/install.sh
$DIR/agents/MoxTabel/configure.py --rest-host "$REST_HOST" --amqp-incoming-host "$DOMAIN" --amqp-incoming-user "$AMQP_USER" --amqp-incoming-pass "$AMQP_PASS" --amqp-incoming-exchange "mox.documentconvert" --amqp-outgoing-host "$DOMAIN" --amqp-outgoing-user "$AMQP_USER" --amqp-outgoing-pass "$AMQP_PASS" --amqp-outgoing-exchange "mox.rest"

$DIR/agents/MoxRestFrontend/install.sh
$DIR/agents/MoxRestFrontend/configure.py --rest-host "$REST_HOST" --amqp-host "$DOMAIN" --amqp-user "$AMQP_USER" --amqp-pass "$AMQP_PASS" --amqp-exchange "mox.rest"

$DIR/agents/MoxDocumentUpload/install.py $REINSTALL_VIRTUALENVS
$DIR/agents/MoxDocumentUpload/configure.py --rest-host "$REST_HOST" --amqp-host "$DOMAIN" --amqp-user "$AMQP_USER" --amqp-pass "$AMQP_PASS" --amqp-exchange "mox.documentconvert"

$DIR/agents/MoxTest/install.sh

$DIR/agents/MoxDocumentDownload/install.py $REINSTALL_VIRTUALENVS
$DIR/agents/MoxDocumentDownload/configure.py --rest-host "$REST_HOST"

$DIR/agents/MoxWiki/install.py
$DIR/agents/MoxWiki/configure.py --amqp-host "$DOMAIN" --amqp-user "$AMQP_USER" --amqp-pass "$AMQP_PASS" --amqp-exchange "mox.notifications" --rest-host "$REST_HOST" --rest-user "$REST_USER" --rest-pass "$REST_PASS"

JAVA_HOME="$OLD_JAVA_HOME"

sudo chown -R mox:mox $DIR
sudo service apache2 reload

echo
echo "Install succeeded!!!"
echo
