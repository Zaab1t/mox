#!/usr/bin/python

import argparse
import os
import sys
import subprocess
from installutils import VirtualEnv, File

DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
MOXDIR = os.path.abspath(DIR + "/../..")

parser = argparse.ArgumentParser(description='Install MoxWiki')

parser.add_argument('-y', '--overwrite-virtualenv', action='store_true')
parser.add_argument('-n', '--keep-virtualenv', action='store_true')

args = parser.parse_args()

# ------------------------------------------------------------------------------

install_log = File("%s/install.log" % DIR)
install_log.touch()

virtualenv = VirtualEnv(DIR + "/python-env")
created = virtualenv.create(args.overwrite_virtualenv, args.keep_virtualenv, install_log.filename)
if created:
    print "Running setup.py"
    virtualenv.run(install_log.filename, "python " + DIR + "/setup.py develop")
    virtualenv.add_moxlib_pointer(MOXDIR)

# ------------------------------------------------------------------------------

subprocess.Popen(['sudo', 'cp', "%s/setup/moxwiki.conf" % DIR, '/etc/init/']).wait()

program_log = File('/var/log/mox/moxwiki.log')
program_log.touch()
program_log.chown('mox')
program_log.chmod('644')

subprocess.Popen(['sudo', 'service', "%moxwiki", 'restart']).wait()
