#!/usr/bin/env python

from __future__ import print_function, absolute_import, unicode_literals

import json
import os
import time

import PyLoRA.LoRA

from . import domain

print('loading...')

cfgpath = os.path.join(os.path.dirname(__file__), 'settings.json')
with open(cfgpath) as fp:
    cfg = json.load(fp)

adcfg = cfg['active-directory']
moxcfg = cfg['mox']
interval = cfg.get('interval', 0)

lora = PyLoRA.LoRA.Lora(moxcfg['host'], moxcfg['user'], moxcfg['password'],
                        cfg.get('logfile', None))

print('making domain...')
domain = domain.Domain(adcfg['domain'], adcfg['host'],
                       adcfg['user'], adcfg['password'])

while interval:
    for obj in domain.poll():
        print(obj)

        if obj.save_to(lora):
            print('saved!')

    time.sleep(interval)
