# encoding: utf-8
""" Small prototype of an applicatin that will allow for mapping
between OIO classes (Klasse) """
import requests

class KlasseMapper(object):
    """ Small prototype of an application that will allow for mapping
    between OIO classes (Klasse) """

    def __init__(self, hostname):
        """
        Init function
        hostname: hostname for the rest interface
        """
        self.hostname = hostname
        self.url = '/klassifikation/klasse/'

    def read_klasse_list(self):
        """ Get a list of all avaiable Klasser
        :return: List of uuid's of all Klasser
        """
        args = {'bvn': '%'}
        response = requests.get(self.hostname + self.url, params=args)
        klasse_list = response.json()['results'][0]
        return klasse_list

    def _create_assymetric_mapping(self, uuid_from, uuid_to):
        """ Map uui_from to uuid_to
        :param uuid_from: The Klasse to recieve the mapping
        :param uuid_to: The klasse that uuid_from will now map to
        :return: Returns True if success
        """
        virkning = {'from': '1801-01-01 12:12:12', 'to': 'infinity'}
        template = {'relationer': {'mapninger':
                                   [{'uuid': '', # Will be filled in
                                     'objekttype': 'Klasse',
                                     'virkning': virkning}]}}
        error_msg = ''
        success = False
        klasse = self.read_klasse(uuid_from)
        mappings = klasse['relationer']['mapninger']
        print(mappings)

    def create_mapping(self, uuid_1, uuid_2, symmetric=True):
        """Maps two uuids
        :param uuid_1: One of the Klasser to be mapped
        :param uuid_2: The other Klasse in the mapping
        :symmetric: If false, the mapping will be one-way - be careful!
        :return: Returns True if success, otherwise False and error message
        """
    
    def read_klasse(self, uuid):
        """
        Read a Klasse from LoRa
        :param resource:    Name of the resource path/entity
        :return:            Returns a dict with the Klasse
        """
        response = requests.get(self.hostname + self.url + uuid)
        klasse = response.json()[uuid][0]['registreringer'][0]
        return klasse

    def read_mappings(self, klasse):
        """ Read all mappings from a klasse
        :param klasse: Klasse object as return by read_klasse, or uuid
        :return: Information about the Klasse ie. Brugervendt nøgle
        """
        actual_mappings = []
        if isinstance(klasse, str):
            klasse = self.read_klasse(klasse)
        try:
            mapping_list = klasse['relationer']['mapninger']
            for mapping in mapping_list:
                actual_mappings.append(mapping['uuid'])
        except KeyError:
            pass
        return actual_mappings

    def basic_klasse_info(self, klasse):
        """ Read human-readable data from Klass
        :param klasse: Klasse object as return by read_klasse, or uuid
        :return: Information about the Klasse ie. Brugervendt nøgle
        """
        if isinstance(klasse, str):
            klasse = self.read_klasse(klasse)
        egenskaber = klasse['attributter']['klasseegenskaber'][0]
        info = egenskaber['brugervendtnoegle']
        return info


def main():
    lora_hostname = 'http://mox-steffen:8080'
    mapper = KlasseMapper(lora_hostname)

    uuid_1 = 'd8043094-6f38-4349-9fbb-dc7c28668fa0'
    uuid_2 = '08857eb8-a2c4-4337-836f-19332f991362'
    #print(mapper._create_assymetric_mapping(uuid_1, uuid_2))
    klasse_list = mapper.read_klasse_list()
    for uuid in klasse_list:
        mapping = mapper.read_mappings(uuid)
        if mapping:
            print(uuid)
            print(mapper.basic_klasse_info(uuid))
            print('-----------')

if __name__ == '__main__':
    main()
