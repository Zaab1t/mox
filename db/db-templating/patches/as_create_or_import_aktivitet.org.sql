-- Copyright (C) 2015 Magenta ApS, http://magenta.dk.
-- Contact: info@magenta.dk.
--
-- This Source Code Form is subject to the terms of the Mozilla Public
-- License, v. 2.0. If a copy of the MPL was not distributed with this
-- file, You can obtain one at http://mozilla.org/MPL/2.0/.

/*
NOTICE: This file is auto-generated using the script: apply-template.py aktivitet as_create_or_import.jinja.sql
*/

CREATE OR REPLACE FUNCTION as_create_or_import_aktivitet(
  aktivitet_registrering AktivitetRegistreringType,
  aktivitet_uuid uuid DEFAULT NULL,
  auth_criteria_arr AktivitetRegistreringType[] DEFAULT NULL
	)
  RETURNS uuid AS 
$$
DECLARE
  aktivitet_registrering_id bigint;
  aktivitet_attr_egenskaber_obj aktivitetEgenskaberAttrType;
  
  aktivitet_tils_status_obj aktivitetStatusTilsType;
  aktivitet_tils_publiceret_obj aktivitetPubliceretTilsType;
  
  aktivitet_relationer AktivitetRelationType;
  auth_filtered_uuids uuid[];
  does_exist boolean;
  new_aktivitet_registrering aktivitet_registrering;
  prev_aktivitet_registrering aktivitet_registrering;
BEGIN

IF aktivitet_uuid IS NULL THEN
    LOOP
    aktivitet_uuid:=uuid_generate_v4();
    EXIT WHEN NOT EXISTS (SELECT id from aktivitet WHERE id=aktivitet_uuid); 
    END LOOP;
END IF;


IF EXISTS (SELECT id from aktivitet WHERE id=aktivitet_uuid) THEN
    does_exist = True;
ELSE

    does_exist = False;
END IF;

IF  (aktivitet_registrering.registrering).livscykluskode<>'Opstaaet'::Livscykluskode and (aktivitet_registrering.registrering).livscykluskode<>'Importeret'::Livscykluskode  and (aktivitet_registrering.registrering).livscykluskode<>'Rettet'::Livscykluskode THEN
  RAISE EXCEPTION 'Invalid livscykluskode[%] invoking as_create_or_import_aktivitet.',(aktivitet_registrering.registrering).livscykluskode USING ERRCODE='MO400';
END IF;


IF NOT does_exist THEN

    INSERT INTO
          aktivitet (ID)
    SELECT
          aktivitet_uuid;
END IF;


/*********************************/
--Insert new registrering

IF NOT does_exist THEN
    aktivitet_registrering_id:=nextval('aktivitet_registrering_id_seq');

    INSERT INTO aktivitet_registrering (
          id,
          aktivitet_id,
          registrering
        )
    SELECT
          aktivitet_registrering_id,
           aktivitet_uuid,
           ROW (
             TSTZRANGE(clock_timestamp(),'infinity'::TIMESTAMPTZ,'[)' ),
             (aktivitet_registrering.registrering).livscykluskode,
             (aktivitet_registrering.registrering).brugerref,
             (aktivitet_registrering.registrering).note
               ):: RegistreringBase ;
ELSE
    -- This is an update, not an import or create
        new_aktivitet_registrering := _as_create_aktivitet_registrering(
             aktivitet_uuid,
             (aktivitet_registrering.registrering).livscykluskode,
             (aktivitet_registrering.registrering).brugerref,
             (aktivitet_registrering.registrering).note);

        aktivitet_registrering_id := new_aktivitet_registrering.id;
END IF;


/*********************************/
--Insert attributes


/************/
--Verification
--For now all declared attributes are mandatory (the fields are all optional,though)

 
IF coalesce(array_length(aktivitet_registrering.attrEgenskaber, 1),0)<1 THEN
  RAISE EXCEPTION 'Savner påkraevet attribut [egenskaber] for [aktivitet]. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;



IF aktivitet_registrering.attrEgenskaber IS NOT NULL and coalesce(array_length(aktivitet_registrering.attrEgenskaber,1),0)>0 THEN
  FOREACH aktivitet_attr_egenskaber_obj IN ARRAY aktivitet_registrering.attrEgenskaber
  LOOP

    INSERT INTO aktivitet_attr_egenskaber (
      brugervendtnoegle,
      aktivitetnavn,
      beskrivelse,
      starttidspunkt,
      sluttidspunkt,
      tidsforbrug,
      formaal,
      virkning,
      aktivitet_registrering_id
    )
    SELECT
     aktivitet_attr_egenskaber_obj.brugervendtnoegle,
      aktivitet_attr_egenskaber_obj.aktivitetnavn,
      aktivitet_attr_egenskaber_obj.beskrivelse,
      aktivitet_attr_egenskaber_obj.starttidspunkt,
      aktivitet_attr_egenskaber_obj.sluttidspunkt,
      aktivitet_attr_egenskaber_obj.tidsforbrug,
      aktivitet_attr_egenskaber_obj.formaal,
      aktivitet_attr_egenskaber_obj.virkning,
      aktivitet_registrering_id
    ;
 

  END LOOP;
END IF;

/*********************************/
--Insert states (tilstande)


--Verification
--For now all declared states are mandatory.
IF coalesce(array_length(aktivitet_registrering.tilsStatus, 1),0)<1  THEN
  RAISE EXCEPTION 'Savner påkraevet tilstand [status] for aktivitet. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;

IF aktivitet_registrering.tilsStatus IS NOT NULL AND coalesce(array_length(aktivitet_registrering.tilsStatus,1),0)>0 THEN
  FOREACH aktivitet_tils_status_obj IN ARRAY aktivitet_registrering.tilsStatus
  LOOP

    INSERT INTO aktivitet_tils_status (
      virkning,
      status,
      aktivitet_registrering_id
    )
    SELECT
      aktivitet_tils_status_obj.virkning,
      aktivitet_tils_status_obj.status,
      aktivitet_registrering_id;

  END LOOP;
END IF;

--Verification
--For now all declared states are mandatory.
IF coalesce(array_length(aktivitet_registrering.tilsPubliceret, 1),0)<1  THEN
  RAISE EXCEPTION 'Savner påkraevet tilstand [publiceret] for aktivitet. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;

IF aktivitet_registrering.tilsPubliceret IS NOT NULL AND coalesce(array_length(aktivitet_registrering.tilsPubliceret,1),0)>0 THEN
  FOREACH aktivitet_tils_publiceret_obj IN ARRAY aktivitet_registrering.tilsPubliceret
  LOOP

    INSERT INTO aktivitet_tils_publiceret (
      virkning,
      publiceret,
      aktivitet_registrering_id
    )
    SELECT
      aktivitet_tils_publiceret_obj.virkning,
      aktivitet_tils_publiceret_obj.publiceret,
      aktivitet_registrering_id;

  END LOOP;
END IF;

/*********************************/
--Insert relations

    INSERT INTO aktivitet_relation (
      aktivitet_registrering_id,
      virkning,
      rel_maal_uuid,
      rel_maal_urn,
      rel_type,
      objekt_type
    )
    SELECT
      aktivitet_registrering_id,
      a.virkning,
      a.uuid,
      a.urn,
      a.relType,
      a.objektType
    FROM unnest(aktivitet_registrering.relationer) a
  ;


/*** Verify that the object meets the stipulated access allowed criteria  ***/
/*** NOTICE: We are doing this check *after* the insertion of data BUT *before* transaction commit, to reuse code / avoid fragmentation  ***/
auth_filtered_uuids:=_as_filter_unauth_aktivitet(array[aktivitet_uuid]::uuid[],auth_criteria_arr); 
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=1 AND auth_filtered_uuids @>ARRAY[aktivitet_uuid]) THEN
  RAISE EXCEPTION 'Unable to create/import aktivitet with uuid [%]. Object does not met stipulated criteria:%',aktivitet_uuid,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401'; 
END IF;
/*********************/


  PERFORM actual_state._amqp_publish_notification('Aktivitet', (aktivitet_registrering.registrering).livscykluskode, aktivitet_uuid);

RETURN aktivitet_uuid;

END;
$$ LANGUAGE plpgsql VOLATILE;


