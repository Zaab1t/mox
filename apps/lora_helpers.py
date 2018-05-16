# encoding: utf-8
import requests
import grequests
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

    def read_klasser(self, uuids):
        """
        Read a list of Klasser from LoRa
        :param uuids:  Name of the resource path/entity
        :return: Returns a list of dicts with the complete Klasse
        """
        klasse_url = self.hostname + '/klassifikation/klasse?uuid='
        complete_urls = []
        i = 0
        param = ''
        for index in range(0, len(uuids)):
            param = param + uuids[index] + '&uuid='
            if i > 94:  # Max length of a request to LoRa
                complete_urls.append(klasse_url + param[:-6])
                i = 0
                param = ''
            else:
                i += 1
        complete_urls.append(klasse_url + param[:-6])

        unsent_request = (grequests.get(url) for url in complete_urls)
        results = grequests.map(unsent_request, size=5)
        klasse_list = []
        klasse_samlinger = [result.json() for result in results]
        for klasse_samling in klasse_samlinger:
            klasse_samling = klasse_samling['results'][0]
            for klasse in klasse_samling:
                uuid = klasse['id']
                klasse = klasse['registreringer'][0]
                klasse['uuid'] = uuid
                klasse_list.append(klasse)
        return klasse_list

    def basic_klasse_info(self, klasser):
        """ Read human-readable data from Klasse
        :param klasse: List of Klasse object as return by read_klasse, or uuids
        :return: Information about the Klasse e. Brugervendtnoegle
        """
        #  If first element is a uuid, all elements are uuids...
        if not isinstance(klasser[0], dict):
            klasser = self.read_klasser(klasser)

        info = []
        for klasse in klasser:
            egenskaber = klasse['attributter']['klasseegenskaber'][0]
            relationer = klasse['relationer']
            try:
                overklasse = relationer['overordnetklasse'][0]['uuid']
            except KeyError:
                overklasse = None
            info.append({'bvn': egenskaber['brugervendtnoegle'],
                         'titel': egenskaber['titel'],
                         'overklasse': overklasse,
                         'uuid': klasse['uuid']})
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

    def delete_all_klasser(self):
        """ Deletes all klasser  """
        klasse_list = self.read_klasse_list()
        deleted_klasser = []
        for klasse in klasse_list:
            deleted_klasser.append(self.delete_klasse(klasse))
        return deleted_klasser

    def _delete_type(self, uuid, url):
        response = requests.delete(self.hostname + url + uuid)
        print(response.text)
        try:
            return_val = response.json()['uuid'] == uuid
        except KeyError:
            return_val = False
        return return_val

    def delete_facet(self, uuid):
        url = '/klassifikation/facet/'
        return self._delete_type(uuid, url)

    def delete_klasse(self, uuid):
        url = '/klassifikation/klasse/'
        return self._delete_type(uuid, url)


def main():
    helper = LoraHelper(settings.host)
    print(helper.read_facet_list())
    raw_list = helper.read_klasse_list()
    klasse_list = helper.basic_klasse_info(raw_list)
    print(len(klasse_list))


if __name__ == '__main__':
    main()
