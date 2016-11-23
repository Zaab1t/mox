#!/usr/bin/env python

from __future__ import print_function, absolute_import, unicode_literals

import json
import os

import PyLoRA.LoRA

from . import domain

print('loading...')

cfgpath = os.path.join(os.path.dirname(__file__), 'settings.json')
with open(cfgpath) as fp:
    cfg = json.load(fp)

adcfg = cfg['config']['active-directory']
moxcfg = cfg['config']['mox']

lora = PyLoRA.LoRA.Lora(moxcfg['host'], moxcfg['user'], moxcfg['password'],
                        cfg.get('verbose', False))

print('making domain...')
domain = domain.Domain(adcfg['domain'], adcfg['host'],
                       adcfg['user'], adcfg['password'])

for obj in domain.objects():
    print('checking {}...'.format(obj))

    if obj.dirty(lora):
        obj.save_to(lora)
        print('saved!')
    else:
        print('up-to-date!')
