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
                         'facet': relationer['facet'][0]['uuid'],
                         'uuid': klasse['uuid']})
        return info

    def read_facet(self, uuid):
        """
        Read a list of Facet from LoRa
        :param uuid:  uuid for the facet
        :return: Returns a dicts with the facet
        """
        response = requests.get(self.hostname + '/klassifikation/facet/' +
                                uuid)
        facet = response.json()[uuid][0]['registreringer'][0]
        return facet
    
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
        try:
            return_val = response.json()['uuid'] == uuid
        except KeyError:
            return_val = False
        return return_val

    def delete_facet(self, uuid):
        """ Delete a specific Facet in LoRa
        :param uuid: The Facet to be deleted
        :return: True if deletion succeeded
        """
        url = '/klassifikation/facet/'
        return self._delete_type(uuid, url)

    def delete_klasse(self, uuid):
        """ Delete a specific Klasse in LoRa
        :param uuid: The Klasse to be deleted
        :return: True if deletion succeeded
        """
        url = '/klassifikation/klasse/'
        return self._delete_type(uuid, url)

    def read_facet_members(self, facet_uuid, klasse_info_list=None):
        """ Read all Klasser that is member of a spcecifik Facet
        :param facet_uuid: The Facet to get the members from
        :return: List of all members
        """
        member_list = []
        if klasse_info_list is None:
            klasse_info_list = self.basic_klasse_info(self.read_klasse_list())
        for klasse in klasse_info_list:
            if klasse['facet'] == facet_uuid:
                member_list.append(klasse['uuid'])
        return member_list

    def read_klasse_sub_members(self, uuid, klasse_info_list=None):
        """ Read a list of the sub_members, ie. Klasser that have Klasse
        as overklasse
        :param uuid: The klasse to read sub-members from
        :param klasse_info_list: If klasse_list already exists, it can be
        provided for better performance
        :return: A list of all sub-members to the Klasse
        """
        klasse_list = []
        if klasse_info_list is None:
            klasse_info_list = self.basic_klasse_info(self.read_klasse_list())
        for klasse in klasse_info_list:
            if klasse['overklasse'] == uuid:
                klasse_list.append(klasse['uuid'])
        return klasse_list

    def read_klasse_full_tree(self, uuid, klasse_info_list=None,
                              klasse_list=[]):
        """ Read all sub-members, including deeper nested levels
        :param uuid: The klasse to read sub-tree from
        :param klasse_info_list: If klasse_list already exists, it can be
        provided for better performance
        :return: A list of all sub-members to the Klasse
        """
        if klasse_info_list is None:
            klasse_info_list = self.basic_klasse_info(self.read_klasse_list())

        sub_list = self.read_klasse_sub_members(uuid, klasse_info_list)
        if sub_list:  # Resursively find all sub-levels
            for klasse in sub_list:
                sub_list = self.read_klasse_full_tree(klasse,
                                                      klasse_info_list,
                                                      klasse_list=klasse_list)
                klasse_list.append(klasse)
        return klasse_list

    def delete_klasse_tree(self, uuid, klasse_info_list=None):
        """ Deletes all klasser and sub-klasser of the klasse
        :param uuid: The klasse to delete, including all children
        :param klasse_info_list: If klasse_list already exists, it can be
        provided for better performance
        :return: A list of all sub-members to the Klasse
        """
        full_sub_list = self.read_klasse_full_tree(uuid, klasse_info_list)
        for klasse in full_sub_list:
            self.delete_klasse(klasse)
        self.delete_klasse(uuid)


def main():
    helper = LoraHelper(settings.host)
    print(len(helper.read_klasse_list()))

    facet_list = helper.read_facet_list()
    print(facet_list)

if __name__ == '__main__':
    main()
