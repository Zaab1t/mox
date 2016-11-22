###############################################################################
                     Synkronisering med `Active Directory`
###############################################################################

Denne pakke indeholder et script til overførsel af data til `LoRA` fra `Active
Directory`. For at køre det udføres::

  $ pip install ldap3 requests
  $ cd .../mox/modules/python/mox
  $ cp ADSync/settings-example.json ADSync/settings.json
  <edit ADSync/settings.json as needed>
  $ python -m ADSync

Overordnet beskrivelse
======================

Målet er at overføre `domæner`, `organisationsenheder`, `sikkerhedsgrupper`,
`brugere` og `it-systemer`.

Indtil videre af basis for overførslen at oplysningerne i Active Directory er
korrekte, og ingen andre skriver til LoRA. Dette tillader to simplificeringer:

1) Vi kan sammeligne tidsstempler snarere end data.
2) Ved enhver ændring kan vi overskrive objekter i LoRA fuldstændig.

Takket være dette kan vi koncentrere os om at konvertere fra AD til LoRA. I
værste fald, hvis andre skrev til AD og vi skulle tilbageføre oplysningerne,
skulle vi inspicere objekterne og resonere om hvilken oplysning der var
“bedst”.

Ydermere er en grundlæggende antagelse at hvert objekt i AD har mindst ét
tilsvarende objekt i LoRA, og at vi importerer det direkte så de to deler UUID.
Dette giver os en triviel kobling mellem de to databaser, så vi undgår at have
en database til synkronisering. Hvis det kræver mere end et objekt i LoRA for
at repræsentere objekter i AD, *skal* vi kunne finde og genkende dem ud fra det
importerede objekt.

Resultatet er at vi kan sammenligne ændringstidspunktet i AD med
registreringstidspunktet i LoRA: hvis AD er ændret efter seneste
registreringsdato i LoRA, må der nødvendigvis være nye oplysninger i AD.[1]

.. [1] Der er dog én lille hage: eftersom data 


Sletning
--------

En særlig udfordring for den nuværende tilgang er hvis objekter slettes i AD.
Ændringer kan vi spørge AD om; sletninger må vi opdage ved at aktivt at
undersøge om alle objekter fortsat eksisterer. Her må vi hente en liste over
hidtidige objekter fra LoRA, sammenligne den med de eksisterende objekter i AD
og notere forskellene.

Dette er ikke implementeret endnu — implementeringen afhænger bl.a. af
størrelsen af AD og om der er begrænsninger på de søgninger vi kan tillade os
at foretage i AD.


Objekttyper
===========

Domænet
-------

Vi overfører indtil videre selve domænet til et Organisation object, under antagelse af
at hver organisation har ét — og kun ét — Active Directory domæne.

Organisationsenheder
--------------------

Overføres til et LoRA `OrganisationEnhed`.


.. Local Variables:
.. mode: rst
.. ispell-local-dictionary: "dansk"
.. coding: utf-8
.. fill-column: 79
.. End:
