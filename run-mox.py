#!/usr/bin/env python2.7
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from __future__ import print_function

import atexit
import contextlib
import imp
import os
import shutil
import subprocess
import sys
import tempfile
import time

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

VENV = os.path.join(BASE_DIR, 'python-env')
VENV_PYTHON = os.path.join(VENV, 'bin', 'python')

if 'PYTHONPATH' in os.environ:
    del os.environ['PYTHONPATH']

if not os.path.isdir(VENV):
    subprocess.check_call([
        sys.executable, '-m' 'virtualenv', '-q', VENV,
    ])
    subprocess.check_call([
        VENV_PYTHON, '-m' 'pip', '-q', 'install', '--isolated',
        'testing.postgresql',
        '-e', os.path.join(BASE_DIR, 'oio_rest'),
    ])

if not sys.executable.startswith(VENV):
    os.execl(VENV_PYTHON, VENV_PYTHON, *sys.argv)

from testing import postgresql

try:
    from oio_rest import settings
except ImportError:
    settings_file = os.path.join(
        BASE_DIR, 'oio_rest', 'oio_rest', 'settings.py',
    )

    shutil.copy(settings_file + '.base', settings_file)

    from oio_rest import settings

try:
    with postgresql.Postgresql(
            base_dir=tempfile.mkdtemp(prefix='mox'),
            postgres_args='-h localhost -F -c logging_collector=off -c synchronous_commit=off -c fsync=off',
    ) as pg:
        dsn = pg.dsn()

        settings.DB_HOST = dsn['host']
        settings.DB_PORT = dsn['port']

        DUMP_FILE = os.path.join(BASE_DIR, 'db', 'dump.sql')

        def psql(**kwargs):
            cmd = [
                'psql',
                '--user', dsn['user'],
                '--host', dsn['host'],
                '--port', str(dsn['port']),
                '--variable', 'ON_ERROR_STOP=1',
                '--output', os.devnull,
                '--no-password',
                '--quiet',
            ]

            for arg, value in kwargs.iteritems():
                cmd += '--' + arg, value,

            subprocess.check_call(cmd)

        psql(command="CREATE USER mox WITH SUPERUSER PASSWORD 'mox'")
        psql(command="CREATE DATABASE mox WITH OWNER = mox")
        psql(command="ALTER DATABASE mox SET search_path TO actual_state,public")

        psql(dbname='mox', file=DUMP_FILE)

        from oio_rest import app

        app.app.run(host='::1',
                    port=int(sys.argv[1]),
                    debug=False,
                    threaded=True,
                    use_reloader=False)
except KeyboardInterrupt:
    pass
finally:
    try:
        shutil.rmtree(pg.base_dir)
    except NameError:
        pass
