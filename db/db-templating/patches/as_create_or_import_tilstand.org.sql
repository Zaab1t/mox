-- Copyright (C) 2015 Magenta ApS, http://magenta.dk.
-- Contact: info@magenta.dk.
--
-- This Source Code Form is subject to the terms of the Mozilla Public
-- License, v. 2.0. If a copy of the MPL was not distributed with this
-- file, You can obtain one at http://mozilla.org/MPL/2.0/.

/*
NOTICE: This file is auto-generated using the script: apply-template.py tilstand as_create_or_import.jinja.sql
*/

CREATE OR REPLACE FUNCTION as_create_or_import_tilstand(
  tilstand_registrering TilstandRegistreringType,
  tilstand_uuid uuid DEFAULT NULL,
  auth_criteria_arr TilstandRegistreringType[] DEFAULT NULL
	)
  RETURNS uuid AS 
$$
DECLARE
  tilstand_registrering_id bigint;
  tilstand_attr_egenskaber_obj tilstandEgenskaberAttrType;
  
  tilstand_tils_status_obj tilstandStatusTilsType;
  tilstand_tils_publiceret_obj tilstandPubliceretTilsType;
  
  tilstand_relationer TilstandRelationType;
  auth_filtered_uuids uuid[];
  does_exist boolean;
  new_tilstand_registrering tilstand_registrering;
  prev_tilstand_registrering tilstand_registrering;
BEGIN

IF tilstand_uuid IS NULL THEN
    LOOP
    tilstand_uuid:=uuid_generate_v4();
    EXIT WHEN NOT EXISTS (SELECT id from tilstand WHERE id=tilstand_uuid); 
    END LOOP;
END IF;


IF EXISTS (SELECT id from tilstand WHERE id=tilstand_uuid) THEN
    does_exist = True;
ELSE

    does_exist = False;
END IF;

IF  (tilstand_registrering.registrering).livscykluskode<>'Opstaaet'::Livscykluskode and (tilstand_registrering.registrering).livscykluskode<>'Importeret'::Livscykluskode  and (tilstand_registrering.registrering).livscykluskode<>'Rettet'::Livscykluskode THEN
  RAISE EXCEPTION 'Invalid livscykluskode[%] invoking as_create_or_import_tilstand.',(tilstand_registrering.registrering).livscykluskode USING ERRCODE='MO400';
END IF;


IF NOT does_exist THEN

    INSERT INTO
          tilstand (ID)
    SELECT
          tilstand_uuid;
END IF;


/*********************************/
--Insert new registrering

IF NOT does_exist THEN
    tilstand_registrering_id:=nextval('tilstand_registrering_id_seq');

    INSERT INTO tilstand_registrering (
          id,
          tilstand_id,
          registrering
        )
    SELECT
          tilstand_registrering_id,
           tilstand_uuid,
           ROW (
             TSTZRANGE(clock_timestamp(),'infinity'::TIMESTAMPTZ,'[)' ),
             (tilstand_registrering.registrering).livscykluskode,
             (tilstand_registrering.registrering).brugerref,
             (tilstand_registrering.registrering).note
               ):: RegistreringBase ;
ELSE
    -- This is an update, not an import or create
        new_tilstand_registrering := _as_create_tilstand_registrering(
             tilstand_uuid,
             (tilstand_registrering.registrering).livscykluskode,
             (tilstand_registrering.registrering).brugerref,
             (tilstand_registrering.registrering).note);

        tilstand_registrering_id := new_tilstand_registrering.id;
END IF;


/*********************************/
--Insert attributes


/************/
--Verification
--For now all declared attributes are mandatory (the fields are all optional,though)

 
IF coalesce(array_length(tilstand_registrering.attrEgenskaber, 1),0)<1 THEN
  RAISE EXCEPTION 'Savner påkraevet attribut [egenskaber] for [tilstand]. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;



IF tilstand_registrering.attrEgenskaber IS NOT NULL and coalesce(array_length(tilstand_registrering.attrEgenskaber,1),0)>0 THEN
  FOREACH tilstand_attr_egenskaber_obj IN ARRAY tilstand_registrering.attrEgenskaber
  LOOP

    INSERT INTO tilstand_attr_egenskaber (
      brugervendtnoegle,
      beskrivelse,
      virkning,
      tilstand_registrering_id
    )
    SELECT
     tilstand_attr_egenskaber_obj.brugervendtnoegle,
      tilstand_attr_egenskaber_obj.beskrivelse,
      tilstand_attr_egenskaber_obj.virkning,
      tilstand_registrering_id
    ;
 

  END LOOP;
END IF;

/*********************************/
--Insert states (tilstande)


--Verification
--For now all declared states are mandatory.
IF coalesce(array_length(tilstand_registrering.tilsStatus, 1),0)<1  THEN
  RAISE EXCEPTION 'Savner påkraevet tilstand [status] for tilstand. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;

IF tilstand_registrering.tilsStatus IS NOT NULL AND coalesce(array_length(tilstand_registrering.tilsStatus,1),0)>0 THEN
  FOREACH tilstand_tils_status_obj IN ARRAY tilstand_registrering.tilsStatus
  LOOP

    INSERT INTO tilstand_tils_status (
      virkning,
      status,
      tilstand_registrering_id
    )
    SELECT
      tilstand_tils_status_obj.virkning,
      tilstand_tils_status_obj.status,
      tilstand_registrering_id;

  END LOOP;
END IF;

--Verification
--For now all declared states are mandatory.
IF coalesce(array_length(tilstand_registrering.tilsPubliceret, 1),0)<1  THEN
  RAISE EXCEPTION 'Savner påkraevet tilstand [publiceret] for tilstand. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;

IF tilstand_registrering.tilsPubliceret IS NOT NULL AND coalesce(array_length(tilstand_registrering.tilsPubliceret,1),0)>0 THEN
  FOREACH tilstand_tils_publiceret_obj IN ARRAY tilstand_registrering.tilsPubliceret
  LOOP

    INSERT INTO tilstand_tils_publiceret (
      virkning,
      publiceret,
      tilstand_registrering_id
    )
    SELECT
      tilstand_tils_publiceret_obj.virkning,
      tilstand_tils_publiceret_obj.publiceret,
      tilstand_registrering_id;

  END LOOP;
END IF;

/*********************************/
--Insert relations

    INSERT INTO tilstand_relation (
      tilstand_registrering_id,
      virkning,
      rel_maal_uuid,
      rel_maal_urn,
      rel_type,
      objekt_type
    )
    SELECT
      tilstand_registrering_id,
      a.virkning,
      a.uuid,
      a.urn,
      a.relType,
      a.objektType
    FROM unnest(tilstand_registrering.relationer) a
  ;


/*** Verify that the object meets the stipulated access allowed criteria  ***/
/*** NOTICE: We are doing this check *after* the insertion of data BUT *before* transaction commit, to reuse code / avoid fragmentation  ***/
auth_filtered_uuids:=_as_filter_unauth_tilstand(array[tilstand_uuid]::uuid[],auth_criteria_arr); 
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=1 AND auth_filtered_uuids @>ARRAY[tilstand_uuid]) THEN
  RAISE EXCEPTION 'Unable to create/import tilstand with uuid [%]. Object does not met stipulated criteria:%',tilstand_uuid,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401'; 
END IF;
/*********************/


  PERFORM actual_state._amqp_publish_notification('Tilstand', (tilstand_registrering.registrering).livscykluskode, tilstand_uuid);

RETURN tilstand_uuid;

END;
$$ LANGUAGE plpgsql VOLATILE;


