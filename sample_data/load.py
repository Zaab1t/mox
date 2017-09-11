from __future__ import print_function

import json
import os
import sys

import requests

TESTS_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(TESTS_DIR)
FIXTURE_DIR = os.path.join(TESTS_DIR, 'fixtures')
LORA_URL = 'http://localhost/'


def _check_response(r):
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if r.status_code == 400 and r.json():
            raise ValueError(r.json()['message'])
        elif r.status_code in (401, 403) and r.json():
            raise EnvironmentError(r.json()['message'])
        else:
            raise

    return r


def create(path, obj, uuid=None):
    if uuid:
        path_string = '{}{}/{}'.format(LORA_URL, path, uuid)
        r = requests.put(path_string, json=obj, verify=False)
        _check_response(r)
        return uuid
    else:
        path_string = '{}{}'.format(LORA_URL, path)
        r = requests.post(path_string, json=obj)
        _check_response(r)
        return r.json()['uuid']


def jsonfile_to_dict(path):
    """
    Reads JSON from resources folder and converts to Python dictionary
    :param path: path to json resource
    :return: dictionary corresponding to the resource JSON
    """
    with open(os.path.join(BASE_DIR, path)) as f:
        return json.load(f)


def get_fixture(fixture_name):
    return jsonfile_to_dict(os.path.join(FIXTURE_DIR, fixture_name))


def load_fixture(path, fixture_name, uuid, verbose=False):
    '''Load a fixture, i.e. a JSON file with the 'fixtures' directory,
    into LoRA at the given path & UUID.

    '''
    if verbose:
        print('creating', path, uuid, file=sys.stderr)
    r = create(path, get_fixture(fixture_name), uuid)
    return r


def arrange_fixtures(items, fixtures, path, formattable_string):
    for itemkey, itemid in items.items():
        fixtures.append((
            path,
            formattable_string.format(itemkey),
            itemid,
        ))


def load_sample_structures(verbose=False):
    '''Inject our test data into LoRA.

    '''
    fixtures = []

    organisation = {
        'AU': '456362c4-0ee4-4e5e-a72c-751239745e62'
    }

    klassifikation = {
        'basic': '10bad33e-2994-4d74-b1b6-cd294ddc454b'
    }

    facet = {
        'basic': 'b8ec5515-7a4f-40b8-85f5-5e8772a372d4'
    }

    organisationsenhed = {
        'root': '2874e1dc-85e6-4269-823a-e1125484dfd3',
        'hum': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
        'samf': 'b688513d-11f7-4efc-b679-ab082a2055d0',
        'fil': '85715fc7-925d-401b-822d-467eb4b163b6',
        'hist': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
        'frem': '04c78fc2-72d2-4d02-b55f-807af19eac48',
    }

    klasse = {
        'afdeling': '32547559-cfc1-4d97-94c6-70b192eff825',
        'fakultet': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
        'institut': 'ca76a441-6226-404f-88a9-31e02e420e52',
    }

    bruger = {
        'anders': '8c949998-f01b-4e7c-953b-8ae4fec475a2',
        'andersine': '013691bc-bbb1-446e-bd0c-82a8be71dbcc',
        'joakim': '43b0ba1d-b613-470b-bb04-a21a2056950e',
    }

    arrange_fixtures(organisation, fixtures, 'organisation/organisation',
                     'create_organisation_{}.json')
    arrange_fixtures(klassifikation, fixtures, 'klassifikation/klassifikation',
                     'create_klassifikation_{}.json')
    arrange_fixtures(facet, fixtures, 'klassifikation/facet',
                     'create_facet_{}.json')
    arrange_fixtures(organisationsenhed, fixtures, 'organisation/organisationenhed',
                     'create_organisationenhed_{}.json')
    arrange_fixtures(klasse, fixtures, 'klassifikation/klasse',
                     'create_klasse_{}.json')
    arrange_fixtures(bruger, fixtures, 'organisation/bruger',
                     'create_bruger_{}.json')

    for path, fixture_name, uuid in fixtures:
        load_fixture(path, fixture_name, uuid, verbose=verbose)


load_sample_structures(verbose=True)
