# encoding: utf-8
""" Small prototype of an applicatin that will allow for mapping
between OIO classes (Klasse) """
import requests
from lora_helpers import LoraHelper
import settings


class KlasseMapper(LoraHelper):
    """ Small prototype of an application that will allow for mapping
    between OIO classes (Klasse)

    Todo: Implement the possibility to remove mappings. Possibly this can be
    done with a small modification of create mapping, by simply not including
    the removed mapping in the iteration"""

    def __init__(self, hostname):
        """
        Init function
        hostname: hostname for the rest interface
        """
        self.hostname = hostname
        self.url = '/klassifikation/klasse/'

    def read_mappings(self, klasser):
        """ Read all mappings from a klasse
        :param klasse: List of Klasse objects as return by read_klasser
        :return: Information about the Klasse ie. Brugervendt nøgle
        """
        actual_mappings = {}
        for klasse in klasser:
            actual_mappings[klasse['uuid']] = []
            try:
                mapping_list = klasse['relationer']['mapninger']
            except KeyError:
                mapping_list = []
            for mapping in mapping_list:
                try:
                    actual_mappings[klasse['uuid']].append(mapping['uuid'])
                except KeyError:
                    pass
        return actual_mappings

    def _create_assymetric_mapping(self, uuid_from, uuid_to):
        """ Map uui_from to uuid_to
        :param uuid_from: The Klasse to recieve the mapping
        :param uuid_to: The klasse that uuid_from will now map to
        :return: Returns True if success
        """
        virkning = {'from': '1801-01-01 12:12:12', 'to': 'infinity'}
        template = {'relationer': {'mapninger':
                                   [{'uuid': uuid_to,
                                     'objekttype': 'Klasse',
                                     'virkning': virkning}]}}

        klasse = self.read_klasser([uuid_from])[0]
        try:
            for mapping in klasse['relationer']['mapninger']:
                template['relationer']['mapninger'].append(mapping)
        except KeyError:
            pass
        response = requests.patch(self.hostname + self.url + uuid_from,
                                  json=template)
        return response.json()['uuid'] == uuid_from

    def create_mapping(self, uuid_1, uuid_2, symmetric=True):
        """Maps two uuids
        :param uuid_1: One of the Klasser to be mapped
        :param uuid_2: The other Klasse in the mapping
        :symmetric: If false, the mapping will be one-way - be careful!
        :return: Returns True if success, otherwise False and error message
        """
        error_msg = ''
        success = False
        klasser = self.read_klasser([uuid_1, uuid_2])
        maps = self.read_mappings(klasser)
        map_1 = maps[uuid_1]
        map_2 = maps[uuid_2]
        if uuid_2 in map_1 or uuid_1 in map_2:
            error_msg = 'Mapping already exists'
        else:
            pass
            success = self._create_assymetric_mapping(uuid_1, uuid_2)
            if success & symmetric:
                success = self._create_assymetric_mapping(uuid_2, uuid_1)
        # Todo: What to do if first mapping succeeds but the other fails?
        return (success, error_msg)


def main():
    lora_hostname = settings.host

    mapper = KlasseMapper(lora_hostname)

    uuid_1 = 'd309e72d-a566-457d-8540-2f7b04739b1a'
    uuid_2 = 'c2604424-2456-4df5-8100-8e01af44f050'
    print(mapper.create_mapping(uuid_1, uuid_2))

    klasse_list = mapper.read_klasse_list()
    klasser = mapper.read_klasser(klasse_list)

    mapping = mapper.read_mappings(klasser)
    for map in mapping:
        if mapping[map]:
            print(map, mapping[map])


if __name__ == '__main__':
    main()
