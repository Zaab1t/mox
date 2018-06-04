from flask import g
import sys
sys.path.append("..")
from lora_helpers import LoraHelper
from mapper import KlasseMapper
import settings


def update_lora():
    g.helper = LoraHelper(settings.host)
    g.mapper = KlasseMapper(settings.host)
    klasse_list = g.helper.read_klasse_list()
    klasse_info = g.helper.basic_klasse_info(klasse_list)

    facet_list = []
    for facet_uuid in g.helper.read_facet_list():
        facet = g.helper.read_facet(facet_uuid)
        egenskaber = facet['attributter']['facetegenskaber'][0]
        info = [facet_uuid,
                egenskaber['beskrivelse'],
                egenskaber['brugervendtnoegle']]
        facet_list.append(info)
    g.facetter = facet_list

    hovedgrupper = []
    for klasse in klasse_info:
        if klasse['overklasse'] is None:
            hovedgrupper.append([klasse['uuid'],
                                 klasse['bvn'],
                                 klasse['titel'],
                                 klasse['facet']])
    g.hovedgrupper = sorted(hovedgrupper, key=lambda tup: tup[1])

    grupper = []
    for klasse in klasse_info:
        if any(klasse['overklasse'] in info_linje
               for info_linje in hovedgrupper):
            grupper.append((klasse['uuid'],
                            klasse['bvn'],
                            klasse['titel'],
                            klasse['overklasse']))
    g.grupper = sorted(grupper, key=lambda tup: tup[1])

    emner = []
    for klasse in klasse_info:
        if any(klasse['overklasse'] in info_linje
               for info_linje in grupper):
            emner.append((klasse['uuid'],
                          klasse['bvn'],
                          klasse['titel'],
                          klasse['overklasse']))
    g.emner = sorted(emner, key=lambda tup: tup[1])
