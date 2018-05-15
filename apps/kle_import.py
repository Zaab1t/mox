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
            data = data.replace('{' + key + '}', value)
        json_data = json.loads(data)
        return json_data

    def read_kle_dict(self, facet='emne', local=True):
        """ Read the entire KLE file
        :param facet: Either 'emne' or 'handlingsfacetter'
        :param local: If True the file is read from local cache
        :return: The document date and the KLE index as a dict
        """
        if facet == 'emne':
            navn = 'emneplan'
        else:
            navn = 'handlefacetter'

        if local:
            with open(navn + '.xml', 'r') as content_file:
                xml_content = content_file.read()
        else:
            url = 'http://clever-gewicht-reduzieren.de/resources/kle/'
            response = requests.get(url + navn)
            xml_content = response.text

        kle_dict = xmltodict.parse(xml_content)
        if facet == 'emne':
            kle_dict = kle_dict['KLE-Emneplan']
            udgivelses_dato = kle_dict['UdgivelsesDato']
            kle_dict = kle_dict['Hovedgruppe']
        else:
            kle_dict = kle_dict['KLE-Handlingsfacetter']
            udgivelses_dato = kle_dict['UdgivelsesDato']
            kle_dict =  kle_dict['HandlingsfacetKategori']
        return (udgivelses_dato, kle_dict)

    def create_facet(self, facet_name):
        """
        Creates a new facet
        :param facet_name: Name of the new facet
        :return: Returns uuid of the new facet
        """
        url = '/klassifikation/facet'
        template = self.load_json_template('facet_opret.json', {})
        bvn = 'brugervendtnoegle'
        template['attributter']['facetegenskaber'][0][bvn] = facet_name

        # TODO: Clean up template and update other relevant fields
        response = requests.post(self.hostname + url, json=template)
        return response.json()['uuid']

    def create_kle_klasse(self, facet, klasse_info, overklasse=None):
        """
        Creates a new Klasse based on KLE
        :param facet: uuid for the korresponding facet
        :param klasse_info: Dict as returned by read_all_*
        :return: Returns uuid of the new klasse
        """
        url = '/klassifikation/klasse'
        template = self.load_json_template('kle_klasse_opret.json',
                                           klasse_info)
        template['relationer']['facet'][0]['uuid'] = facet
        if overklasse is not None:
            template['relationer']['overordnetklasse'][0]['uuid'] = overklasse
        response = requests.post(self.hostname + url, json=template)
        return response.json()['uuid']

    def read_all_hovedgrupper(self, kle_dict, facet='emne'):
        """ Read all Hovedgrupper from KLE
        :param kle_dict: A dictinary containing KLE
        :param facet: Either 'emne' or 'handlingsfacetter'
        :return: Dict with index as as key and
        (HovedgruppeTitel, HovedgruppeNr) as value
        """
        name = 'Hovedgruppe' if facet == 'emne' else 'HandlingsfacetKategori'
        hovedgrupper = {}
        for i in range(0, len(kle_dict)):
            titel = kle_dict[i][name + 'Titel']
            hovedgrupper[i] = (titel, kle_dict[i][name + 'Nr'])
        return hovedgrupper

    def read_all_from_hovedgruppe(self, kle_dict, hovedgruppe_index,
                                  facet='emne'):
        """ Read all relevant fields from a Hovedgruppe - this can
        easily be extended if more info turns out to be relevant
        :param kle_dict: A dictinary containing KLE
        :param hovedgruppe_index: Index for the wanted Hovedgruppe
        :param facet: Either 'emne' or 'handlingsfacetter'
        :return: Dict with relevant info
        """
        name = 'Hovedgruppe' if facet == 'emne' else 'HandlingsfacetKategori'
        hovedgruppe = kle_dict[hovedgruppe_index]
        hovedgruppe_info = {}
        hovedgruppe_info['titel'] = hovedgruppe[name + 'Titel']
        adm_info = hovedgruppe[name + 'AdministrativInfo']
        hovedgruppe_info['oprettetdato'] = adm_info['OprettetDato']
        hovedgruppe_info['nummer'] = hovedgruppe[name + 'Nr']
        # TODO: Der findes også info om rettet-dato, er dette relevant?
        return hovedgruppe_info

    def read_all_grupper(self, kle_dict, hovedgruppe, facet='emne'):
        """ Read all Grupper from a KLE Hovedgruppe
        :param kle_dict: A dictinary containing KLE
        :param hovedgruppe: A KLE Hovedgruppe index to be retrieved
        :param facet: Either 'emne' or 'handlingsfacetter'
        :return: Dict with index as key and (GruppeTitel, GruppeNr) as value
        """
        name = 'Gruppe' if facet == 'emne' else 'Handlingsfacet'
        grupper = {}
        gruppe_liste = kle_dict[hovedgruppe][name]
        for i in range(0, len(gruppe_liste)):
            grupper[i] = (gruppe_liste[i][name + 'Titel'],
                          gruppe_liste[i][name + 'Nr'][3:])
        return grupper

    def read_all_from_gruppe(self, kle_dict, hovedgruppe, gruppe,
                             facet='emne'):
        """ Read all relevant fields from a Gruppe - this can
        easily be extended if more info turns out to be relevant
        :param kle_dict: A dictinary containing KLE
        :param hovedgruppe: Index for the wanted Hovedgruppe
        :param gruppe: Index for the wanted Gruppe
        :param facet: Either 'emne' or 'handlingsfacetter'
        :return: Dict with relevant info
        """
        name = 'Gruppe' if facet == 'emne' else 'Handlingsfacet'
        slice_val = 3 if facet == 'emne' else 1
        gruppe = kle_dict[hovedgruppe][name][gruppe]
        gruppe_info = {}
        gruppe_info['titel'] = gruppe[name + 'Titel']
        adm_info = gruppe[name + 'AdministrativInfo']
        gruppe_info['oprettetdato'] =  adm_info['OprettetDato']
        gruppe_info['nummer'] = gruppe[name + 'Nr'][slice_val:]
        return gruppe_info

    def read_all_emner(self, kle_dict, hovedgruppe, gruppe):
        """ Read all Emner from a KLE Gruppe
        :param kle_dict: A dictinary containing KLE
        :param hovedgruppe: The KLE Hovedgruppe index containing the Gruppe
        :param GruppeNr: The KLE Gruppe index to be retrieved
        :return: Dict with index as key and (EmneTitel, EmneNr) as value
        """
        emner = {}
        emne_liste = kle_dict[hovedgruppe]['Gruppe'][gruppe]['Emne']
        for i in range(0, len(emne_liste)):
            try:
                emner[i] = (emne_liste[i]['EmneTitel'],
                            emne_liste[i]['EmneNr'][6:])
            except KeyError: # If only one element, there is no list
                emner[0] = (emne_liste['EmneTitel'],
                            emne_liste['EmneNr'][6:])

        return emner

    def read_all_from_emne(self, kle_dict, hovedgruppe, gruppe, emne):
        """ Read all relevant fields from a Gruppe - this can
        easily be extended if more info turns out to be relevant
        :param kle_dict: A dictinary containing KLE
        :param hovedgruppe: Index for the wanted Hovedgruppe
        :param gruppe: Index for the wanted Gruppe
        :param gruppe: emne for the wanted Emne
        :return: Dict with relevant info
        """
        try:
            emne = kle_dict[hovedgruppe]['Gruppe'][gruppe]['Emne'][emne]
        except KeyError:  # If only one element, there is no list
            emne = kle_dict[hovedgruppe]['Gruppe'][gruppe]['Emne']
        emne_info = {}
        emne_info['titel'] = emne['EmneTitel']
        adm_info = emne['EmneAdministrativInfo']
        emne_info['oprettetdato'] =  adm_info['OprettetDato']
        emne_info['nummer'] = emne['EmneNr'][6:]
        return emne_info


def main():
    lora_hostname = settings.host
    kle = KleUploader(lora_hostname)

    kle_content = kle.read_kle_dict(facet='emne')
    print('Document date: ' + kle_content[0])
    kle_dict = kle_content[1]

    emne_facet_uuid = kle.create_facet('Emne')
    #emne_facet_uuid = '46c5ce8f-f9a9-4f1b-b0cc-93076168771d'

    hovedgrupper = (kle.read_all_hovedgrupper(kle_dict))
    for hoved_index in hovedgrupper:
        hoved_info = kle.read_all_from_hovedgruppe(kle_dict, hoved_index)
        print(hoved_info['nummer'] + ': ' + hoved_info['titel'])
        # Create hovedgruppe
        hoved_uuid = kle.create_kle_klasse(emne_facet_uuid, hoved_info)

        grupper = kle.read_all_grupper(kle_dict, hoved_index)
        for gruppe_index in grupper:
            gruppe_info = kle.read_all_from_gruppe(kle_dict, hoved_index,
                                                   gruppe_index)
            print(hoved_info['nummer'] + '.' + gruppe_info['nummer'] + ': ' +
                  gruppe_info['titel'])
            # Create gruppe
            gruppe_uuid = kle.create_kle_klasse(emne_facet_uuid, gruppe_info,
                                                hoved_uuid)
            emner = kle.read_all_emner(kle_dict, hoved_index, gruppe_index)
            for emne_index in emner:
                emne_info = kle.read_all_from_emne(kle_dict, hoved_index,
                                                   gruppe_index, emne_index)
                print(hoved_info['nummer'] + '.' + gruppe_info['nummer'] +
                      '.' + emne_info['nummer'] + ': ' + emne_info['titel'])
                # Create emne
                emne_uuid = kle.create_kle_klasse(emne_facet_uuid, emne_info,
                                                  gruppe_uuid)

    kle_content = kle.read_kle_dict(facet='handling')
    print('Document date: ' + kle_content[0])
    kle_dict = kle_content[1]

    funktion_uuid = kle.create_facet('Funktion')
    # funktion_uuid = '7c971657-438b-4cf2-a157-65a2cd7ccdd4'
    hovedgrupper = (kle.read_all_hovedgrupper(kle_dict, facet='handling'))
    for hoved_index in hovedgrupper:
        hoved_info = kle.read_all_from_hovedgruppe(kle_dict, hoved_index,
                                                   facet='handling')
        print(hoved_info['nummer'] + ': ' + hoved_info['titel'])
        hoved_uuid = kle.create_kle_klasse(emne_facet_uuid, hoved_info)

        grupper = kle.read_all_grupper(kle_dict, hoved_index, facet='handling')
        for gruppe_index in grupper:
            gruppe_info = kle.read_all_from_gruppe(kle_dict, hoved_index,
                                                   gruppe_index,
                                                   facet='handling')
            print(hoved_info['nummer'] + gruppe_info['nummer'] + ': ' +
                  gruppe_info['titel'])
            # Create gruppe
            gruppe_uuid = kle.create_kle_klasse(emne_facet_uuid, gruppe_info,
                                                hoved_uuid)


if __name__ == '__main__':
    main()