CREATE OR REPLACE FUNCTION ACTUAL_STATE_CREATE_BRUGER(
    Attributter BrugerEgenskaberType[],
    Tilstande BrugerTilstandType[]
--   TODO: Accept relations
)
  RETURNS Bruger AS $$
DECLARE
  brugerUUID uuid;
  brugerRegistreringID BIGINT;
  result Bruger;
BEGIN
    brugerUUID := uuid_generate_v4();
--   Create Bruger
    INSERT INTO Bruger (ID) VALUES(brugerUUID);
--   Create Registrering
--   TODO: Insert Note into registrering?
    brugerRegistreringID := ACTUAL_STATE_NEW_REGISTRATION_BRUGER(
        brugerUUID, 'Opstaaet', NULL
    );
--   Loop through attributes and add them to the registration
  DECLARE
    attr BrugerEgenskaberType;
  BEGIN
  FOREACH attr in ARRAY Attributter
    LOOP
      INSERT INTO BrugerEgenskaber (BrugerRegistreringID, Virkning, BrugervendtNoegle, Brugernavn, Brugertype)
    VALUES (brugerRegistreringID, attr.Virkning, attr.BrugervendtNoegle,
            attr.Brugernavn, attr.Brugertype);
    END LOOP;
  END;

--   Loop through states and add them to the registration
  DECLARE
    state BrugerTilstandType;
  BEGIN
    FOREACH state in ARRAY Tilstande
    LOOP
      INSERT INTO BrugerTilstand (BrugerRegistreringID, Virkning, Status)
      VALUES (brugerRegistreringID, state.Virkning, state.Status);
    END LOOP;
  END;

  SELECT * FROM Bruger WHERE ID = brugerUUID INTO result;
  RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION ACTUAL_STATE_READ_BRUGER(
    ID UUID,
    VirkningPeriod TSTZRANGE,
    RegistreringPeriod TSTZRANGE,
    filteredAttributesRef REFCURSOR,
    filteredStatesRef REFCURSOR
)
  RETURNS SETOF REFCURSOR AS $$
DECLARE
  inputID UUID := ID;
  result BrugerRegistrering;
BEGIN
  -- Get the whole registrering which overlaps with the registrering (system)
  -- time period.
  SELECT * FROM BrugerRegistrering
    JOIN Bruger ON Bruger.ID = BrugerRegistrering.BrugerID
  WHERE Bruger.ID = inputID AND
        -- && operator means ranges overlap
        (BrugerRegistrering.Registrering).TimePeriod && RegistreringPeriod
    -- We only want the first result
    LIMIT 1
  INTO result;

  -- Filter the attributes' registrering by the virkning (application) time
  -- period
  OPEN filteredAttributesRef FOR SELECT * FROM brugeregenskaber
  WHERE brugerregistreringid = result.id AND
        (virkning).TimePeriod && VirkningPeriod;

  ---
  OPEN filteredStatesRef FOR SELECT * FROM brugertilstand
  WHERE brugerregistreringid = result.id AND
        (virkning).TimePeriod && VirkningPeriod;
  RETURN;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION ACTUAL_STATE_NEW_REGISTRATION_BRUGER(
  inputID UUID,
  LivscyklusKode LivscyklusKode,
  BrugerRef UUID,
  doCopy BOOLEAN DEFAULT FALSE
) RETURNS BIGINT AS $$
DECLARE
  registreringTime        TIMESTAMPTZ := transaction_timestamp();
  newRegistreringID       BIGINT;
  oldBrugerRegistreringID BIGINT;
BEGIN
-- Update previous Registrering's time range to end now, exclusive
  UPDATE BrugerRegistrering
    SET Registrering.TimePeriod =
      TSTZRANGE(LOWER((Registrering).TimePeriod), registreringTime)
    WHERE BrugerID = inputID AND upper((Registrering).TimePeriod) = 'infinity'
    RETURNING ID INTO oldBrugerRegistreringID;
--   Create Registrering starting from now until infinity
  INSERT INTO BrugerRegistrering (BrugerID, Registrering) VALUES (
    inputID,
    ROW (TSTZRANGE(registreringTime, 'infinity',
                   '[]'), LivscyklusKode, BrugerRef)
  )
  RETURNING ID
    INTO newRegistreringID;

  IF doCopy
  THEN
    DECLARE
      r RECORD;
    BEGIN
      FOR r in SELECT virkning, brugervendtnoegle, brugernavn, brugertype
               FROM brugeregenskaber WHERE brugerregistreringid =
                                           oldBrugerRegistreringID
      LOOP
        INSERT INTO BrugerEgenskaber (BrugerRegistreringID, Virkning, BrugervendtNoegle, Brugernavn, Brugertype)
        VALUES (newRegistreringID, r.Virkning, r.BrugervendtNoegle,
                r.Brugernavn, r.Brugertype);
      END LOOP;
    END;

    DECLARE
      r RECORD;
    BEGIN
      FOR r in SELECT virkning, status
               FROM brugertilstand WHERE brugerregistreringid =
                                           oldBrugerRegistreringID
      LOOP
        INSERT INTO BrugerTilstand (BrugerRegistreringID, Virkning, Status)
        VALUES (newRegistreringID, r.Virkning, r.Status);
      END LOOP;
    END;
  END IF;

  RETURN newRegistreringID;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION ACTUAL_STATE_UPDATE_BRUGER(
  inputID UUID,
  Attributter BrugerEgenskaberType[],
  Tilstande BrugerTilstandType[]
)
  RETURNS BrugerRegistrering AS $$
DECLARE
  brugerRegistreringID BIGINT;
  result BrugerRegistrering;
BEGIN
  brugerRegistreringID := ACTUAL_STATE_NEW_REGISTRATION_BRUGER(
      inputID, 'Rettet', NULL
  );
--   Loop through attributes and add them to the registration
  DECLARE
    attr BrugerEgenskaberType;
  BEGIN
    FOREACH attr in ARRAY Attributter
    LOOP
      INSERT INTO BrugerEgenskaber (BrugerRegistreringID, Virkning, BrugervendtNoegle, Brugernavn, Brugertype)
      VALUES (brugerRegistreringID, attr.Virkning, attr.BrugervendtNoegle,
              attr.Brugernavn, attr.Brugertype);
    END LOOP;
  END;

--   Loop through states and add them to the registration
  DECLARE
    state BrugerTilstandType;
  BEGIN
    FOREACH state in ARRAY Tilstande
    LOOP
      INSERT INTO BrugerTilstand (BrugerRegistreringID, Virkning, Status)
      VALUES (brugerRegistreringID, state.Virkning, state.Status);
    END LOOP;
  END;

  SELECT * FROM BrugerRegistrering WHERE ID = brugerRegistreringID INTO result;
  RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION ACTUAL_STATE_DELETE_BRUGER(
  inputID UUID
)
  RETURNS BrugerRegistrering AS $$
DECLARE
  brugerRegistreringID BIGINT;
  result BrugerRegistrering;
BEGIN
  brugerRegistreringID := ACTUAL_STATE_NEW_REGISTRATION_BRUGER(
      inputID, 'Slettet', NULL, doCopy := TRUE
  );

  SELECT * FROM BrugerRegistrering WHERE ID = brugerRegistreringID INTO result;
  RETURN result;
END;
$$ LANGUAGE plpgsql;
