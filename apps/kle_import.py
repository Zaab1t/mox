# encoding: utf-8
""" Script to import KLE into LoRa to allow easy access to relevant
test data """
import requests
import json
#Facetter

#Emne: http://clever-gewicht-reduzieren.de/resources/kle/emneplan
#Funktion: http://clever-gewicht-reduzieren.de/resources/kle/handlingsfacetter

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

        #TODO: Clean up template and update other relevant fields
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

        #TODO: Clean up template and update with all info from KLE
        #response = requests.post(self.hostname + url, json=template)
        #return response.json()['uuid']


def main():
    lora_hostname = 'http://mox-steffen:8080'
    kle = KleUploader(lora_hostname)

    #emne_uuid = kle.create_facet('Emne')
    #funktion_uuid = kle.create_facet('Funktion')
    test_uuid = kle.create_facet('Klyf')
    print(kle.create_klasse(test_uuid))
    
if __name__ == '__main__':
    main()
