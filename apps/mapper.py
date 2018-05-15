# encoding: utf-8
""" Small prototype of an applicatin that will allow for mapping
between OIO classes (Klasse) """
import requests
from lora_helpers import LoraHelper
import settings

class KlasseMapper(LoraHelper):
    """ Small prototype of an application that will allow for mapping
    between OIO classes (Klasse) """

    def __init__(self, hostname):
        """
        Init function
        hostname: hostname for the rest interface
        """
        self.hostname = hostname
        self.url = '/klassifikation/klasse/'


    def read_mappings(self, klasse):
        """ Read all mappings from a klasse
        :param klasse: Klasse object as return by read_klasse, or uuid
        :return: Information about the Klasse ie. Brugervendt nøgle
        """
        actual_mappings = []
        if isinstance(klasse, unicode):
            klasse = self.read_klasse(klasse)
        try:
            mapping_list = klasse['relationer']['mapninger']
        except KeyError:
            mapping_list = []
        for mapping in mapping_list:
            try:
                actual_mappings.append(mapping['uuid'])
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

        klasse = self.read_klasse(uuid_from)
        print(self.basic_klasse_info(klasse))
        for mapping in klasse['relationer']['mapninger']:
            template['relationer']['mapninger'].append(mapping)
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
        map_1 = self.read_mappings(uuid_1)
        map_2 = self.read_mappings(uuid_2)
        if uuid_2 in map_1 or uuid_1 in map_2:
            error_msg = 'Mapping already exists'
        else:
            success = self._create_assymetric_mapping(uuid_1, uuid_2)
            if success & symmetric:
                success = self._create_assymetric_mapping(uuid_2, uuid_1)
            # Todo: What to do if first mapping succeeds but the other fails?
        return (success, error_msg)


def main():
    lora_hostname = settings.host

    mapper = KlasseMapper(lora_hostname)

    uuid_1 = 'ee8dd627-9ff1-47c2-b900-aa3c214a31ee'
    uuid_2 = 'a88aa93b-8edc-46ab-bad7-6535f9b765e5'

    #print(mapper.create_mapping(uuid_1, uuid_2))

    klasse_list = mapper.read_klasse_list()
    for uuid in klasse_list:
        mapping = mapper.read_mappings(uuid)
        if not mapping:
            print(uuid)
            print(mapper.basic_klasse_info(uuid))
            print('-----------')


if __name__ == '__main__':
    main()
