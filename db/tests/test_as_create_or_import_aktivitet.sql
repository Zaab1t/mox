-- Copyright (C) 2015 Magenta ApS, http://magenta.dk.
-- Contact: info@magenta.dk.
--
-- This Source Code Form is subject to the terms of the Mozilla Public
-- License, v. 2.0. If a copy of the MPL was not distributed with this
-- file, You can obtain one at http://mozilla.org/MPL/2.0/.

--SELECT * FROM runtests('test'::name);
CREATE OR REPLACE FUNCTION test.test_as_create_or_import_aktivitet()
RETURNS SETOF TEXT LANGUAGE plpgsql AS 
$$
DECLARE 
	new_uuid1 uuid;
	registrering aktivitetRegistreringType;
	actual_registrering RegistreringBase;
	virkEgenskaber Virkning;
	virkEgenskaber2 Virkning;
	virkAnsvarligklasse Virkning;
	virkResultatklasse1 Virkning;
	virkResultatklasse2 Virkning;
	virkDeltagerklasse1 Virkning;
	virkDeltagerklasse2 Virkning;
	virkPubliceret Virkning;
	virkStatus Virkning;
	aktivitetEgenskab aktivitetEgenskaberAttrType;
	aktivitetEgenskab2 aktivitetEgenskaberAttrType;
	aktivitetStatus aktivitetStatusTilsType;
	aktivitetPubliceret aktivitetPubliceretTilsType;
	aktivitetRelAnsvarligklasse aktivitetRelationType;
	aktivitetRelResultatklasse1 aktivitetRelationType;
	aktivitetRelResultatklasse2 aktivitetRelationType;
	aktivitetRelDeltagerklasse1 aktivitetRelationType;
	aktivitetRelDeltagerklasse2 aktivitetRelationType;
	
	uuidAnsvarligklasse uuid :='f7109356-e87e-4b10-ad5d-36de6e3ee09f'::uuid;
	uuidResultatklasse1 uuid :='b7160ce6-ac92-4752-9e82-f17d9e1e52ce'::uuid;


	--uuidResultatklasse2 uuid :='08533179-fedb-4aa7-8902-ab34a219eed9'::uuid;
	urnResultatklasse2 text:='urn:isbn:0451450523'::text;
	uuidDeltagerklasse1 uuid :='f7109356-e87e-4b10-ad5d-36de6e3ee09d'::uuid;
	uuidDeltagerklasse2 uuid :='28533179-fedb-4aa7-8902-ab34a219eed1'::uuid;
	uuidRegistrering uuid :='1f368584-4c3e-4ba4-837b-da2b1eee37c9'::uuid;
	actual_publiceret_virk virkning;
	actual_publiceret_value aktivitetStatusTils;
	actual_publiceret aktivitetStatusTilsType;
	actual_relationer aktivitetRelationType[];
	uuid_to_import uuid :='a1819cce-043b-447f-ba5e-92e6a75df918'::uuid;
	uuid_returned_from_import uuid;
	read_Aktivitet1 AktivitetType;
	expected_aktivitet1 AktivitetType;
BEGIN


virkEgenskaber :=	ROW (
	'[2015-05-12, 2015-06-10)' :: TSTZRANGE,
          uuid_generate_v4(),
          'Bruger',
          'NoteEx1'
          ) :: Virkning
;

virkEgenskaber2 :=	ROW (
	'[2015-06-10, infinity)' :: TSTZRANGE,
          uuid_generate_v4(),
          'Bruger',
          'NoteEx90'
          ) :: Virkning
;

virkAnsvarligklasse :=	ROW (
	'[2015-05-11, infinity)' :: TSTZRANGE,
          uuid_generate_v4(),
          'Bruger',
          'NoteEx2'
          ) :: Virkning
;

virkResultatklasse1 :=	ROW (
	'[2015-05-10, infinity)' :: TSTZRANGE,
          uuid_generate_v4(),
          'Bruger',
          'NoteEx3'
          ) :: Virkning
;


virkResultatklasse2 :=	ROW (
	'[2015-05-10, 2016-05-10)' :: TSTZRANGE,
          uuid_generate_v4(),
          'Bruger',
          'NoteEx4'
          ) :: Virkning
;

virkPubliceret := ROW (
	'[2015-05-18, infinity)' :: TSTZRANGE,
          uuid_generate_v4(),
          'Bruger',
          'NoteEx10'
) :: Virkning
;

virkstatus := ROW (
	'[2016-12-18, infinity)' :: TSTZRANGE,
          uuid_generate_v4(),
          'Bruger',
          'NoteEx20'
) :: Virkning
;

virkDeltagerklasse1 :=	ROW (
	'[2015-04-10, infinity)' :: TSTZRANGE,
          uuid_generate_v4(),
          'Bruger',
          'NoteEx23'
          ) :: Virkning
;


virkDeltagerklasse2 :=	ROW (
	'[2015-06-10, 2016-05-10)' :: TSTZRANGE,
          uuid_generate_v4(),
          'Bruger',
          'NoteEx12'
          ) :: Virkning
;

aktivitetRelAnsvarligklasse := ROW (
	'ansvarligklasse'::aktivitetRelationKode
	,virkAnsvarligklasse
	,uuidAnsvarligklasse
	,null
	,'Klasse'
	,567 --NOTICE: Should be replace in by import function
	,null --aktoerAttr
) :: aktivitetRelationType
;


aktivitetRelResultatklasse1 := ROW (
	'resultatklasse'::aktivitetRelationKode,
		virkResultatklasse1,
	uuidResultatklasse1,
	null,
	'Klasse'
	,768 --NOTICE: Should be replace in by import function
	,null --aktoerAttr
) :: aktivitetRelationType
;



aktivitetRelResultatklasse2 := ROW (
	'resultatklasse'::aktivitetRelationKode,
		virkResultatklasse2,
	null,
	urnResultatklasse2,
	'Klasse'
	,800 --NOTICE: Should be replace in by import function
	,null --aktoerAttr
) :: aktivitetRelationType
;



aktivitetRelDeltagerklasse1 := ROW (
	'deltagerklasse'::aktivitetRelationKode,
		virkDeltagerklasse1,
	uuidDeltagerklasse1,
	null,
	'Klasse'
	,7268 --NOTICE: Should be replace in by import function
	,null --aktoerAttr
) :: aktivitetRelationType
;



aktivitetRelDeltagerklasse2 := ROW (
	'deltagerklasse'::aktivitetRelationKode,
		virkDeltagerklasse2,
	uuidDeltagerklasse2,
	null,
	'Klasse'
	,3 --NOTICE: Should be replace in by import function
	,null --aktoerAttr
) :: aktivitetRelationType
;



aktivitetStatus := ROW (
virkStatus,
'Aktiv'::AktivitetStatusTils
):: aktivitetStatusTilsType
;

aktivitetPubliceret := ROW (
virkPubliceret,
'Normal'::AktivitetPubliceretTils
)::aktivitetPubliceretTilsType;


aktivitetEgenskab := ROW (
 'aktivitet_1_brugervendtnoegle',
 'aktivitet_1_aktivitetnavn',
 'aktivitet_1_beskrivelse',
 '2017-02-25 17:00'::timestamptz,  --'starttidspunkt_aktivitet_1' --text
'2017-02-27 08:00'::timestamptz, -- sluttidspunkt,
  INTERVAL '0000-00 03 02:30:00.0', --tidsforbrug
 'aktivitet_1_formaal'
,virkEgenskaber
) :: aktivitetEgenskaberAttrType
;

aktivitetEgenskab2 := ROW (
 'aktivitet_2_brugervendtnoegle',
 'aktivitet_2_aktivitetnavn',
 'aktivitet_2_beskrivelse',
 '2016-04-20 10:00'::timestamptz,  --'starttidspunkt_aktivitet_1' --text
'2017-02-27 12:00'::timestamptz, -- sluttidspunkt,
  INTERVAL '0000-00 01 04:00:01.0', --tidsforbrug
 'aktivitet_2_formaal'
,virkEgenskaber2
) :: aktivitetEgenskaberAttrType
;


registrering := ROW (
	ROW (
	NULL,
	'Opstaaet'::Livscykluskode,
	uuidRegistrering,
	'Test Note 4') :: RegistreringBase
	,
	ARRAY[aktivitetStatus]::aktivitetStatusTilsType[],
	ARRAY[aktivitetPubliceret]::AktivitetPubliceretTilsType[],
ARRAY[aktivitetEgenskab,aktivitetEgenskab2]::aktivitetEgenskaberAttrType[],
ARRAY[aktivitetRelAnsvarligklasse,aktivitetRelResultatklasse1,aktivitetRelResultatklasse2,aktivitetRelDeltagerklasse1,aktivitetRelDeltagerklasse2]) :: aktivitetRegistreringType
;


--raise notice 'to be written aktivitet 1:%',to_json(registrering);

new_uuid1 := as_create_or_import_aktivitet(registrering);

RETURN NEXT ok(true,'No errors running as_create_or_import_aktivitet');


read_Aktivitet1 := as_read_aktivitet(new_uuid1,
	null, --registrering_tstzrange
	null --virkning_tstzrange
	);
raise notice 'read_Aktivitet1:%',to_json(read_Aktivitet1);

expected_aktivitet1:=ROW(
		new_uuid1,
		ARRAY[
			ROW(
			(read_Aktivitet1.registrering[1]).registrering
			,ARRAY[aktivitetStatus]::aktivitetStatusTilsType[]
			,ARRAY[aktivitetPubliceret]::aktivitetPubliceretTilsType[]
			,ARRAY[aktivitetEgenskab,aktivitetEgenskab2]::aktivitetEgenskaberAttrType[]
			,ARRAY[
				ROW (
				'deltagerklasse'::aktivitetRelationKode,
					virkDeltagerklasse2,
				uuidDeltagerklasse2,
				null,
				'Klasse'
				,2 --NOTICE: Should be replace in by import function
				,ROW (null,null,null,null)::AktivitetAktoerAttr   --NOTICE: empty composites will be removed in python layer --aktoerAttr
			) :: aktivitetRelationType
				,
				ROW (
					'resultatklasse'::aktivitetRelationKode,
						virkResultatklasse1,
					uuidResultatklasse1,
					null,
					'Klasse'
					,1 --NOTICE: Was replaced
					,ROW (null,null,null,null)::AktivitetAktoerAttr  --aktoerAttr
				) :: aktivitetRelationType
				,
				ROW (
				'deltagerklasse'::aktivitetRelationKode,
					virkDeltagerklasse1,
				uuidDeltagerklasse1,
				null,
				'Klasse'
				,1 --NOTICE: Was replaced  by import function
				,ROW (null,null,null,null)::AktivitetAktoerAttr  --aktoerAttr
			) :: aktivitetRelationType
			,
				ROW (
				'ansvarligklasse'::aktivitetRelationKode
				,virkAnsvarligklasse
				,uuidAnsvarligklasse
				,null
				,'Klasse'
				,NULL --NOTICE: Was replaced
				,ROW (null,null,null,null)::AktivitetAktoerAttr  --aktoerAttr
			) :: aktivitetRelationType
			,ROW (
				'resultatklasse'::aktivitetRelationKode,
					virkResultatklasse2,
				null,
				urnResultatklasse2,
				'Klasse'
				,2 --NOTICE: Was replaced
				,ROW (null,null,null,null)::AktivitetAktoerAttr  --aktoerAttr
			) :: aktivitetRelationType

				]::AktivitetRelationType[]
			)::AktivitetRegistreringType
			]::AktivitetRegistreringType[]
		)::AktivitetType
;

raise notice 'expected_aktivitet1:%',to_json(expected_aktivitet1);



RETURN NEXT IS(
	read_Aktivitet1,
	expected_aktivitet1
	,'test create aktivitet #1'
);







END;
$$;