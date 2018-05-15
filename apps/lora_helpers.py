# encoding: utf-8
import requests
import settings

class LoraHelper(object):
    """ Small set of function to help with LoRa maintenance """

    def __init__(self, hostname):
        """
        Init function
        :param hostname: hostname for the rest interface
        """
        self.hostname = hostname
        self.request = requests.Session()

    def _read_type_list(self, url):
        """ Get a list of a uuids of a specific type
        :param url: Url for the wanted list type
        :return: The complete list of uuids for the type
        """
        args = {'bvn': '%'}
        response = requests.get(self.hostname + url, params=args)
        klasse_list = response.json()['results'][0]
        return klasse_list
        
    def read_klasse_list(self):
        """ Get a list of all avaiable Klasser
        :return: List of uuid's of all Klasser
        """
        url = '/klassifikation/klasse/'
        return self._read_type_list(url)

    def read_klasse(self, uuid):
        """
        Read a Klasse from LoRa
        :param resource:    Name of the resource path/entity
        :return:            Returns a dict with the Klasse
        """
        url = '/klassifikation/klasse/'
        #response = requests.get(self.hostname + url + uuid)
        response = self.request.get(self.hostname + url + uuid)
        klasse = response.json()[uuid][0]['registreringer'][0]
        return klasse

    def basic_klasse_info(self, klasse):
        """ Read human-readable data from Klass
        :param klasse: Klasse object as return by read_klasse, or uuid
        :return: Information about the Klasse ie. Brugervendtnoegle
        """
        if isinstance(klasse, unicode):
            klasse = self.read_klasse(klasse)
        egenskaber = klasse['attributter']['klasseegenskaber'][0]
        info = egenskaber['brugervendtnoegle']
        return info   
    
    def read_facet_list(self):
        """ Get a list of all avaiable Facetter
        :return: List of uuid's of all Facetter
        """
        url = '/klassifikation/facet/'
        return self._read_type_list(url)

    def delete_all_facetter(self):
        """ Deletes all Facetter  """
        facet_list = self.read_facet_list()
        for facet in facet_list:
            self.delete_facet(facet)

    def delte_all_klasser(self):
        """ Deletes all Facetter  """

    def delete_facet(self, uuid):
        url = '/klassifikation/facet/'
        response = requests.delete(self.hostname + url + uuid)
        try:
            return_val = response.json()['uuid'] == uuid
        except KeyError:
            return_val = False
        return return_val

def main():
    helper = LoraHelper(settings.host)
    #print(helper.delete_facet('81b80fa7-b71b-4d33-b528-cae03820875'))
    #print(helper.read_facet_list())
    #print(helper.delete_all_facetter())
    klasse_list = helper.read_klasse_list()
    for klasse in klasse_list[0:100]:
        print(helper.basic_klasse_info(klasse))


if __name__ == '__main__':
    main()
