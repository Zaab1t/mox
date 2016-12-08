#!/usr/bin/env python

from __future__ import print_function, absolute_import, unicode_literals

import json
import os
import time

import PyLoRA.LoRA

from . import domain
from . import auth

print('loading...')

cfgpath = os.path.join(os.path.dirname(__file__), 'settings.json')
with open(cfgpath) as fp:
    cfg = json.load(fp)

idp_url = \
    'https://{}/adfs/services/trust/13/UsernameMixed'.format(cfg['host'])
auth = auth.SAMLTokenAuth(cfg['host'], '@'.join((cfg['user'], cfg['domain'])),
                          cfg['password'], cfg['moxurl'])

lora = PyLoRA.LoRA.Lora(cfg['moxurl'], auth, cfg.get('logfile', None))

print('making domain...')
domain = domain.Domain(cfg['domain'], cfg['host'],
                       cfg['user'], cfg['password'])

interval = cfg.get('interval', 0)

while interval:
    for obj in domain.poll():
        print(obj)

        if obj.save_to(lora):
            print('saved!')

    time.sleep(interval)
