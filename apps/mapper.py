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

    def create_assymetric_mapping(self, uuid_from, uuid_to):
        virkning = {'from': '1801-01-01 12:12:12', 'to': 'infinity'}
        template = {'relationer': {'mapninger':
                                   [{'uuid': '', # Will be filled in
                                     'objekttype': 'Klasse',
                                     'virkning': virkning}]}}

        pass
    
    def read_klasse(self, uuid):
        """
        Read a Klasse from LoRa
        :param resource:    Name of the resource path/entity
        :return:            Returns a dict with the Klasse
        """
        response = requests.get(self.hostname + self.url + uuid)
        klasse = response.json()[uuid][0]['registreringer'][0]
        return klasse

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

    klasse_list = mapper.read_klasse_list()
    for uuid in klasse_list:
        print(mapper.basic_klasse_info(uuid))


if __name__ == '__main__':
    main()
