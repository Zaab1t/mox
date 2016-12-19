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
    'wiki_host': "https://%s" % domain
}

parser = argparse.ArgumentParser(description='Install MoxWiki')

parser.add_argument('-y', '--overwrite-virtualenv', action='store_true')
parser.add_argument('-n', '--keep-virtualenv', action='store_true')

parser.add_argument('--wiki-host', action='store')
parser.add_argument('--wiki-user', action='store')
parser.add_argument('--wiki-pass', action='store')

parser.add_argument('--amqp-host', action='store')
parser.add_argument('--amqp-user', action='store')
parser.add_argument('--amqp-pass', action='store')
parser.add_argument('--amqp-queue', action='store')

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

configfile = DIR + "/moxwiki/settings.conf"

config_map = [
    ('wiki_host', 'moxwiki.wiki.host'),
    ('wiki_user', 'moxwiki.wiki.username'),
    ('wiki_pass', 'moxwiki.wiki.password'),
    ('amqp_host', 'moxwiki.amqp.host'),
    ('amqp_user', 'moxwiki.amqp.username'),
    ('amqp_pass', 'moxwiki.amqp.password'),
    ('amqp_queue', 'moxwiki.amqp.queue'),
    ('rest_host', 'moxwiki.rest.host'),
    ('rest_user', 'moxwiki.rest.username'),
    ('rest_pass', 'moxwiki.rest.password')
]
config = Config(configfile)

config.prompt(config_map, args, defaults)

config.save()

# ------------------------------------------------------------------------------

proc = subprocess.Popen(['sudo', 'cp', "%s/setup/moxwiki.conf" % DIR, '/etc/init/'])
proc.wait()
