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
    helper = LoraHelpers(settings.host)
    print(helper.delete_facet('81b80fa7-b71b-4d33-b528-cae03820875'))
    print(helper.read_facet_list())
    print(helper.delete_all_facetter())

if __name__ == '__main__':
    main()
