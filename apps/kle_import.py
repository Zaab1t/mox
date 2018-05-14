# encoding: utf-8
""" Script to import KLE into LoRa to allow easy access to relevant
test data """
import requests
import json
import xmltodict
import settings

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

    def load_json_template(self, filename, replace_dict=None):
        """ Load a json file and return as dict
        :param filename: Filename for the json file
        :replace_dict: Dict with parameters to be replace in the template
        :return: The json file formateed as a python dictionary
        """
        with open(filename) as f:
            data = f.read()
        for key, value in replace_dict.items():
            data = data.replace('{' + key +'}', value)
        json_data = json.loads(data)
        return json_data

    def read_kle_dict(self, local=True):
        """ Read the entire KLE file
        :param local: If True the file is read from local cache
        :return: The document date and the KLE index as a dict
        """
        if local:
            with open('emneplan.xml', 'r') as content_file:
                xml_content = content_file.read()
        else:
            url  = 'http://clever-gewicht-reduzieren.de/resources/kle/emneplan'
            response = requests.get(url)
            xml_content =response.text

        kle_dict = xmltodict.parse(xml_content)['KLE-Emneplan']
        udgivelses_dato = kle_dict['UdgivelsesDato']
        kle_dict = kle_dict['Hovedgruppe']  # Everything except date is here
        return (udgivelses_dato, kle_dict)
    
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

    def create_kle_klasse(self, facet, klasse_info, overklasse=None):
        """
        Creates a new Klasse based on KLE
        :param facet: uuid for the korresponding facet
        :param name: Name for the Klasse
        :return: Returns uuid of the new klasse
        """
        url = '/klassifikation/klasse'
        print(klasse_info)
        dato = klasse_info['oprettetdato']

        template = self.load_json_template('kle_klasse_opret.json',
                                           klasse_info)
        template['relationer']['facet'][0]['uuid'] = facet
        if overklasse is not None:
            template['relationer']['overordnetklasse'][0]['uuid'] = overklasse
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

    def read_all_from_hovedgruppe(self, kle_dict, hovedgruppe_nummer):
        """ Read all relevant fields from a Hovedgruppe - this can
        easily be extended if more info turns out to be relevant
        :param kle_dict: A dictinary containing KLE
        :param hovedgruppe: Index for the wanted Hovedgruppe
        :return: Dict with relevant info 
        """
        for i in range(0, len(kle_dict)):
            if int(kle_dict[i]['HovedgruppeNr']) == hovedgruppe_nummer:
                break
        hovedgruppe = kle_dict[i]
        hovedgruppe_info = {}
        hovedgruppe_info['titel'] = hovedgruppe['HovedgruppeTitel']
        adm_info = hovedgruppe['HovedgruppeAdministrativInfo']
        hovedgruppe_info['oprettetdato'] =  adm_info['OprettetDato']
        hovedgruppe_info['nummer'] = str(hovedgruppe_nummer).zfill(2)
        # TODO: Der findes også info om rettet-dato, er dette relevant?
        return hovedgruppe_info

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
    lora_hostname = settings.host
    kle = KleUploader(lora_hostname)

    kle_content = kle.read_kle_dict()
    print('Document date: ' + kle_content[0])
    kle_dict = kle_content[1]
    
    #emne_uuid = kle.create_facet('Emne')
    emne_uuid = '46c5ce8f-f9a9-4f1b-b0cc-93076168771d'

    hovedgrupper = (kle.read_all_hovedgrupper(kle_dict))
    for hovedgruppe in hovedgrupper:
        print(str(hovedgruppe).zfill(2), hovedgrupper[hovedgruppe])
        klasse_info = kle.read_all_from_hovedgruppe(kle_dict, hovedgruppe)
    print(kle.create_kle_klasse(emne_uuid, klasse_info))
    
    # funktion_uuid = kle.create_facet('Funktion')


    # print(kle.read_gruppe(kle_dict, 2))

    #print(kle.read_emner(kle_dict, 2, 5))




if __name__ == '__main__':
    main()
