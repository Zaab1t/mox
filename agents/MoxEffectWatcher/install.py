#!/usr/bin/python

import argparse
import os
import sys
import subprocess
import socket
from installutils import Config, VirtualEnv

domain = socket.getfqdn(socket.gethostname())
DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
MOXDIR = os.path.abspath(DIR + "/../..")

defaults = {
    'amqp_host': domain,
    'rest_host': "https://%s" % domain,
    'amqp_exchange_in': 'mox.notifications',
    'amqp_exchange_out': 'mox.notifications'
}

parser = argparse.ArgumentParser(description='Install MoxEffectWatcher')

parser.add_argument('-y', '--overwrite-virtualenv', action='store_true')
parser.add_argument('-n', '--keep-virtualenv', action='store_true')

parser.add_argument('--amqp-host', action='store')
parser.add_argument('--amqp-user', action='store')
parser.add_argument('--amqp-pass', action='store')
parser.add_argument('--amqp-exchange-in', action='store')
parser.add_argument('--amqp-exchange-out', action='store')

parser.add_argument('--rest-host', action='store')
parser.add_argument('--rest-user', action='store')
parser.add_argument('--rest-pass', action='store')

args = parser.parse_args()

# ------------------------------------------------------------------------------

logfilename = "%s/install.log" % DIR
fp = open(logfilename, 'w')
fp.close()

virtualenv = VirtualEnv(DIR + "/python-env")
created = virtualenv.create(args.overwrite_virtualenv, args.keep_virtualenv, logfilename)
if created:
    print "Running setup.py"
    virtualenv.run(logfilename, "python " + DIR + "/setup.py develop")
    virtualenv.add_moxlib_pointer(MOXDIR)

# ------------------------------------------------------------------------------

configfile = DIR + "/moxeffectwatcher/settings.conf"

config_map = [
    ('amqp_host', 'moxeffectwatcher.amqp.host'),
    ('amqp_user', 'moxeffectwatcher.amqp.username'),
    ('amqp_pass', 'moxeffectwatcher.amqp.password'),
    ('amqp_exchange_in', 'moxeffectwatcher.amqp.exchange_in'),
    ('amqp_exchange_out', 'moxeffectwatcher.amqp.exchange_out'),
    ('rest_host', 'moxeffectwatcher.rest.host'),
    ('rest_user', 'moxeffectwatcher.rest.username'),
    ('rest_pass', 'moxeffectwatcher.rest.password')
]
config = Config(configfile)

print "\n"
config.prompt(config_map, args, defaults)

config.save()

# ------------------------------------------------------------------------------

proc = subprocess.Popen(['sudo', 'cp', "%s/setup/moxeffectwatcher.conf" % DIR, '/etc/init/'])
proc.wait()
