#!/usr/bin/env python

from PyOIO.OIOCommon import Virkning, OIOEntity, OIORegistrering, InvalidOIOException, requires_load
from PyOIO.OIOCommon import OIOEgenskab, OIOEgenskabContainer


class ItSystem(OIOEntity):
    """It-system
    from: Specifikation af serviceinterface for Organisation. Version 1.1

    This class implements an object model reflecting the OIO It-system class.
    It contains two things only:
    - A GUID
    - A list of ItSystemRegistrering objects
    """

    ENTITY_CLASS = 'Itsystem'
    EGENSKABER_KEY = 'itsystemegenskaber'
    GYLDIGHED_KEY = 'itsystemgyldighed'
    basepath = '/organisation/itsystem'

    def __init__(self, lora, id):
        """
        Arguments:
        lora:   Lora - the Lora handler object
        ID:     string - the GUID uniquely representing the ItSystem
        """
        super(ItSystem, self).__init__(lora, id)


@ItSystem.registrering_class
class ItSystemRegistrering(OIORegistrering):
    """It-system registrering
    from: Specifikation af serviceinterface for Organisation. Version 1.1

    This class implements a Python object model reflecting the above for the
    It-system registreringclass. The meat of data about an It system is
    contained in these.

    The ItSystem class will contain a list of 1..N of these.
    """

    # ---- Egenskaber ----

    @property
    def itsystemnavn(self):
        return self.get_egenskab('itsystemnavn')

    @property
    def name(self):
        return self.itsystemnavn

    @property
    def itsystemtype(self):
        return self.get_egenskab('itsystemtype')

    @property
    def type(self):
        return self.itsystemtype

    @property
    def konfigurationreference(self):
        return self.get_egenskab('konfigurationreference')


@ItSystem.egenskab_class
class ItSystemEgenskab(OIOEgenskab):

    def __init__(self, registrering, data):
        super(ItSystemEgenskab, self).__init__(registrering, data)
        self.itsystemnavn = data.get('itsystemnavn')
        self.itsystemtype = data.get('itsystemtype')
        self.konfigurationreference = data.get('konfigurationreference')

    @property
    def name(self):
        return self.itsystemnavn
