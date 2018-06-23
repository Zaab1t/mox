#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

from tests import util


class TestVirkning(util.TestCase):
    URL = '/klassifikation/klassifikation'

    def setUp(self):
        super(TestVirkning, self).setUp()
        self.klassifikation = {
            'attributter': {
                'klassifikationegenskaber': []
            },
            'tilstande': {
                'klassifikationpubliceret': [
                    {
                        'publiceret': 'Publiceret',
                        'virkning': {
                            'from': '-infinity',

                            # from_included should be False...
                            # We should fix this in the DB layer
                            'from_included': True,

                            'to': 'infinity',
                            'to_included': False
                        }
                    }

                ]
            }
        }

    @unittest.skip('from_included should be False for minus inf lower bound')
    def test_from_and_to_included_false_for_infinite_interval(self):
        """
        Equivalence classes covered: [116][120][124]
        See https://github.com/magenta-aps/mox/doc/Systematic_testing.rst for
        further details

        LoRa input:  ---------------------------
        LoRa output: ---------------------------
        """
        self.klassifikation['attributter']['klassifikationegenskaber'].append(
            {
                'brugervendtnoegle': 'bvn1',
                'virkning': {
                    'from': '-infinity',
                    'to': 'infinity',
                    'to_included': False
                }
            }
        )
        r = self.perform_request(self.URL, json=self.klassifikation)

        # Check response
        self.assert201(r)

        # Check persisted data
        self.klassifikation['livscykluskode'] = 'Opstaaet'
        self.klassifikation['attributter']['klassifikationegenskaber'][0][
            'virkning']['from_included'] = False

        self.assertQueryResponse(
            self.URL,
            self.klassifikation,
            uuid=r.json['uuid']
        )

    @unittest.skip('Not possible to set from_included to False')
    def test_from_and_to_included_false_for_open_interval(self):
        """
        Equivalence classes covered: [117][121]
        See https://github.com/magenta-aps/mox/doc/Systematic_testing.rst for
        further details

        LoRa input:  (------------------------)
        LoRa output: (------------------------)
        """

        self.klassifikation['attributter']['klassifikationegenskaber'].append(
            {
                'brugervendtnoegle': 'bvn1',
                'virkning': {
                    'from': '2010-01-01 12:00:00+01',
                    'from_included': False,
                    'to': '2020-01-01 12:00:00+01',
                    'to_included': False
                }
            }
        )
        r = self.perform_request(self.URL, json=self.klassifikation)

        # Check response
        self.assert201(r)

        # Check persisted data
        self.klassifikation['livscykluskode'] = 'Opstaaet'
        self.assertQueryResponse(
            self.URL,
            self.klassifikation,
            uuid=r.json['uuid']
        )

    @unittest.skip('Not possible to set to_included to True')
    def test_from_and_to_included_true_for_closed_interval(self):
        """
        Equivalence classes covered: [118][122][123]
        See https://github.com/magenta-aps/mox/doc/Systematic_testing.rst for
        further details

        LoRa input:  [-----------------------]
        LoRa output: [-----------------------]
        """

        self.klassifikation['attributter']['klassifikationegenskaber'].append(
            {
                'brugervendtnoegle': 'bvn1',
                'virkning': {
                    'from': '2010-01-01 12:00:00+01',
                    'from_included': True,
                    'to': '2020-01-01 12:00:00+01',
                }
            }
        )
        r = self.perform_request(self.URL, json=self.klassifikation)

        # Check response
        self.assert201(r)

        # Check persisted data
        self.klassifikation['livscykluskode'] = 'Opstaaet'
        self.klassifikation['attributter']['klassifikationegenskaber'][0][
            'virkning']['to_included'] = True

        self.assertQueryResponse(
            self.URL,
            self.klassifikation,
            uuid=r.json['uuid']
        )

    @unittest.skip('LoRa accepts inconsistent "from" and "from_included"')
    def test_from_included_cannot_be_true_when_lower_boundary_minus_inf(self):
        """
        Equivalence classes covered: [115]
        See https://github.com/magenta-aps/mox/doc/Systematic_testing.rst for
        further details

        LoRa input:  ---------------------------
        LoRa output: ---------------------------
        """
        self.klassifikation['attributter']['klassifikationegenskaber'].append(
            {
                'brugervendtnoegle': 'bvn1',
                'virkning': {
                    'from': '-infinity',
                    'from_included': True,
                    'to': 'infinity',
                }
            }
        )
        r = self.perform_request(self.URL, json=self.klassifikation)

        # Check response
        self.assert400(r)

    @unittest.skip('LoRa accepts inconsistent "to" and "to_included"')
    def test_to_included_cannot_be_true_when_upper_boundary_infinity(self):
        """
        Equivalence classes covered: [119]
        See https://github.com/magenta-aps/mox/doc/Systematic_testing.rst for
        further details

        LoRa input:  ---------------------------
        LoRa output: ---------------------------
        """
        self.klassifikation['attributter']['klassifikationegenskaber'].append(
            {
                'brugervendtnoegle': 'bvn1',
                'virkning': {
                    'from': '-infinity',
                    'to': 'infinity',
                    'to_included': True
                }
            }
        )
        r = self.perform_request(self.URL, json=self.klassifikation)

        # Check response
        self.assert400(r)
