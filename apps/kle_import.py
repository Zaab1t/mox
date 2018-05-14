# encoding: utf-8
""" Script to import KLE into LoRa to allow easy access to relevant
test data """
import requests
import json
import xmltodict

# Facetter
# Emne: http://clever-gewicht-reduzieren.de/resources/kle/emneplan
# Funktion: http://clever-gewicht-reduzieren.de/resources/kle/handlingsfacetter

# WARNING: Consider the trustworthiness of the XML file!
# Safety considerations do exist! https://docs.python.org/3/library/xml.html


class KleUploader(object):
    """ Script to import KLE into LoRa to allow easy access to relevant
    test data """

    def __init__(self, hostname):
        """
        Init function
        hostname: hostname for the rest interface
        """
        self.hostname = hostname

    def load_json_template(self, filename):
        """ Load a json file and return as dict
        :param filename: Filename for the json file
        :return: The json file formateed as a python dictionary
        """
        with open(filename) as json_data:
            data = json.load(json_data)
        return data

    def create_facet(self, facet_name):
        """
        Creates a new facet
        :param facet_name: Name of the new facet
        :return: Returns uuid of the new facet
        """
        url = '/klassifikation/facet'
        template = self.load_json_template('facet_opret.json')
        bvn = 'brugervendtnoegle'
        template['attributter']['facetegenskaber'][0][bvn] = facet_name

        # TODO: Clean up template and update other relevant fields
        response = requests.post(self.hostname + url, json=template)
        return response.json()['uuid']

    def create_klasse(self, facet):
        """
        Creates a new Klasse
        :param facet: uuid for the korresponding facet
        :return: Returns uuid of the new klasse
        """
        url = '/klassifikation/klasse'
        template = self.load_json_template('klasse_opret.json')
        template['relationer']['facet'][0]['uuid'] = facet

        # TODO: Clean up template and update with all info from KLE
        response = requests.post(self.hostname + url, json=template)
        return response.json()['uuid']

    def read_all_hovedgrupper(self, kle_dict):
        """ Read all Hovedgrupper from KLE
        :param kle_dict: A dictinary containing KLE
        :return: Dict with HovedgruppeNr as key and HovedgruppeTitel as value
        """
        hovedgrupper = {}
        for i in range(0, len(kle_dict)):
            titel = kle_dict[i]['HovedgruppeTitel']
            hovedgrupper[int(kle_dict[i]['HovedgruppeNr'])] = titel
        return hovedgrupper

    def read_gruppe(self, kle_dict, hovedgruppe):
        """ Read all Grupper from a KLE Hovedgruppe
        :param kle_dict: A dictinary containing KLE
        :param hovedgruppe: A KLE HovedgruppeNr to be retrieved
        :return: Dict with GruppeNr as key and GruppeTitel as value
        """
        grupper = {}
        gruppe_liste = kle_dict[hovedgruppe]['Gruppe']
        for i in range(0, len(gruppe_liste)):
            gruppe_nummer = int(gruppe_liste[i]['GruppeNr'][3:])
            grupper[gruppe_nummer] = gruppe_liste[i]['GruppeTitel']
        return grupper

    def read_emner(self, kle_dict, hovedgruppe, gruppe):
        """ Read all Emner from a KLE Gruppe
        :param kle_dict: A dictinary containing KLE
        :param hovedgruppe: The KLE HovedgruppeNR containing the Gruppe
        :param GruppeNr: The KLE Gruppe to be retrieved
        :return: Dict with EmneNr as key and EmneTitel as value
        """
        emner = {}
        print(gruppe)
        emne_liste = kle_dict[hovedgruppe]['Gruppe'][gruppe]['Emne']
        for i in range(0, len(emne_liste)):
            emne_nummer = int(emne_liste[i]['EmneNr'][6:])
            emner[emne_nummer] = emne_liste[i]['EmneTitel']
        return emner


def main():
    lora_hostname = 'http://mox-steffen:8080'
    kle = KleUploader(lora_hostname)

    # emne_uuid = kle.create_facet('Emne')
    # funktion_uuid = kle.create_facet('Funktion')
    # test_uuid = kle.create_facet('Klyf')
    # print(kle.create_klasse(test_uuid))

    # emneplan  = 'http://clever-gewicht-reduzieren.de/resources/kle/emneplan'
    # response = requests.get(emneplan)
    # print(response.text)

    with open('emneplan.xml', 'r') as content_file:
        content = content_file.read()
    kle_dict = xmltodict.parse(content)['KLE-Emneplan']
    print('KLE udgivelsesdato: ' + kle_dict['UdgivelsesDato'])
    kle_dict = kle_dict['Hovedgruppe']  # Everything except date is here

    # hovedgrupper = (kle.read_all_hovedgrupper(elt))
    # for hovedgruppe in hovedgrupper:
    #     print(str(hovedgruppe).zfill(2), hovedgrupper[hovedgruppe])

    # print(kle.read_gruppe(kle_dict, 2))

    print(kle.read_emner(kle_dict, 2, 5))

    """
    #elt indeholder nu en liste med alle 36 hovedgrupper
    print(type(elt[0]))
    #for key in elt[0].keys():
    #    print(key)
    print(type(elt[0]['Gruppe']))
    #print(elt[0]['Gruppe'][0])
    for key in elt[0]['Gruppe'][0].keys():
        print(key)
    print(elt[0]['Gruppe'][0]['Emne'])
    """


if __name__ == '__main__':
    main()
