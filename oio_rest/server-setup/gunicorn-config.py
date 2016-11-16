import multiprocessing

bind = ':8000'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
preload_app = True

user = 'mox'
group = 'mox'

accesslog = '/var/log/oio_rest/access.log'
errorlog = '/var/log/oio_rest/error.log'

proc_name = 'oio_rest'
pidfile = '/var/run/oio_rest.pid'

raw_env = [
    'NO_VENV=1',
]
