#!/usr/bin/env python

from __future__ import print_function

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


print('fetch token...')
lora.obtain_token()

print('making domain...')
domain = domain.Domain(adcfg['domain'], adcfg['host'],
                       adcfg['user'], adcfg['password'])

print('processing domain {}...'.format(adcfg['domain']))
if domain.dirty(lora):
    domain.save_to(lora)
    print('saved!')
else:
    print('up-to-date!')

for group in domain.groups():
    print('processing group {}...'.format(group.name))

    if group.dirty(lora):
        group.save_to(lora)
        print('saved!')
    else:
        print('up-to-date!')

for user in domain.groups():
    print('processing user {}...'.format(user.name))

    if user.dirty(lora):
        user.save_to(lora)
        print('saved!')
    else:
        print('up-to-date!')
