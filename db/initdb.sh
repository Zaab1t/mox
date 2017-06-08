#!/bin/bash -e
set -b

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
MOXDIR=$(cd $DIR/..; pwd)
PYTHON="$MOXDIR/python-env/bin/python"

function superdo_sql
{
    if test -n "$SUPER_USER" -a "$USER" != "$SUPER_USER"
    then
        sudo PGDATABASE=$PGDATABASE PGUSER=postgres PGPASSWORD= PGHOST=$PGHOST PGPORT=$PGPORT -u postgres psql -q "$@"
    else
        psql -q "$@"
    fi
}

cd $DIR
source ./config.sh

export PGDATABASE="$MOX_DB"
export PGUSER="$MOX_DB_USER"
export PGPASSWORD="$MOX_DB_PASSWORD"
export PGPORT="$MOX_DB_PORT"
export PGHOST="$MOX_DB_HOST"

sudo -u postgres createdb $MOX_DB
sudo -u postgres createuser $MOX_DB_USER
sudo -u postgres psql -q -c "GRANT ALL ON DATABASE $MOX_DB TO $MOX_DB_USER"
sudo -u postgres psql -q -c "ALTER USER $MOX_DB_USER WITH PASSWORD '$MOX_DB_PASSWORD';"

superdo_sql -f basis/dbserver_prep.sql

psql -q -c "CREATE SCHEMA actual_state AUTHORIZATION $MOX_DB_USER "
superdo_sql -c "ALTER database $MOX_DB SET search_path TO actual_state,public;"
superdo_sql -c "ALTER database $MOX_DB SET DATESTYLE to 'ISO, YMD';" #Please notice that the db-tests are run, using a different datestyle
superdo_sql -c "ALTER database $MOX_DB SET INTERVALSTYLE to 'sql_standard';" 

psql -q -c "CREATE SCHEMA test AUTHORIZATION $MOX_DB_USER "
psql -q -f basis/common_types.sql
psql -q -f funcs/_index_helper_funcs.sql
psql -q -f funcs/_subtract_tstzrange.sql
psql -q -f funcs/_subtract_tstzrange_arr.sql
psql -q -f funcs/_as_valid_registrering_livscyklus_transition.sql
psql -q -f funcs/_as_search_match_array.sql
psql -q -f funcs/_as_search_ilike_array.sql
psql -q -f funcs/_json_object_delete_keys.sql





cd ./db-templating/

./generate-sql-tbls-types-funcs-for-oiotype.sh

#Apply patches 
cd ./generated-files/
#klasse
patch --silent --fuzz=3 -i  ../patches/dbtyper-specific_klasse.sql.diff
patch --silent --fuzz=3 -i  ../patches/tbls-specific_klasse.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_create_or_import_klasse.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_list_klasse.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_search_klasse.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_update_klasse.sql.diff
patch --silent --fuzz=3 -i  ../patches/_remove_nulls_in_array_klasse.sql.diff
#sag
patch --silent --fuzz=3 -i  ../patches/tbls-specific_sag.sql.diff
patch --silent --fuzz=3 -i  ../patches/dbtyper-specific_sag.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_list_sag.sql.diff
patch --silent --fuzz=3 -i  ../patches/_remove_nulls_in_array_sag.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_create_or_import_sag.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_update_sag.sql.diff
patch --silent --fuzz=3 -i  ../patches/json-cast-functions_sag.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_search_sag.sql.diff
#dokument
patch --silent --fuzz=3 -i  ../patches/dbtyper-specific_dokument.sql.diff
patch --silent --fuzz=3 -i  ../patches/tbls-specific_dokument.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_create_or_import_dokument.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_update_dokument.sql.diff
patch --silent --fuzz=3 -i  ../patches/_remove_nulls_in_array_dokument.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_list_dokument.sql.diff
patch --silent --fuzz=3 -i  ../patches/json-cast-functions_dokument.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_search_dokument.sql.diff
#aktivitet
patch --silent --fuzz=3 -i  ../patches/tbls-specific_aktivitet.sql.diff
patch --silent --fuzz=3 -i  ../patches/dbtyper-specific_aktivitet.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_list_aktivitet.sql.diff
patch --silent --fuzz=3 -i  ../patches/_remove_nulls_in_array_aktivitet.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_create_or_import_aktivitet.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_update_aktivitet.sql.diff
patch --silent --fuzz=3 -i  ../patches/json-cast-functions_aktivitet.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_search_aktivitet.sql.diff
#indsats
patch --silent --fuzz=3 -i  ../patches/tbls-specific_indsats.sql.diff
patch --silent --fuzz=3 -i  ../patches/dbtyper-specific_indsats.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_list_indsats.sql.diff
patch --silent --fuzz=3 -i  ../patches/_remove_nulls_in_array_indsats.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_create_or_import_indsats.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_update_indsats.sql.diff
patch --silent --fuzz=3 -i  ../patches/json-cast-functions_indsats.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_search_indsats.sql.diff
#tilstand
patch --silent --fuzz=3 -i  ../patches/tbls-specific_tilstand.sql.diff
patch --silent --fuzz=3 -i  ../patches/dbtyper-specific_tilstand.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_list_tilstand.sql.diff
patch --silent --fuzz=3 -i  ../patches/_remove_nulls_in_array_tilstand.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_create_or_import_tilstand.sql.diff
patch --silent --fuzz=3 -i  ../patches/as_update_tilstand.sql.diff
patch --silent --fuzz=3 -i  ../patches/json-cast-functions_tilstand.sql.diff
patch --silent --fuzz=3 -i ../patches/as_search_tilstand.sql.diff

cd ..
fi

oiotypes=$($PYTHON -m oio_rest.db_helpers)

templates1=( dbtyper-specific tbls-specific _remove_nulls_in_array )


for oiotype in $oiotypes
do
	for template in "${templates1[@]}"
	do
		psql -q -f ./generated-files/${template}_${oiotype}.sql
	done	
done

#Extra functions depending on templated data types 
psql -q -f ../funcs/_ensure_document_del_exists_and_get.sql
psql -q -f ../funcs/_ensure_document_variant_exists_and_get.sql
psql -q -f ../funcs/_ensure_document_variant_and_del_exists_and_get_del.sql
psql -q -f ../funcs/_as_list_dokument_varianter.sql


templates2=(  _as_get_prev_registrering _as_create_registrering as_update  as_create_or_import  as_list as_read as_search json-cast-functions _as_filter_unauth )


for oiotype in $oiotypes
do
	for template in "${templates2[@]}"
	do
		psql -q -f ./generated-files/${template}_${oiotype}.sql
	done	
done

cd ..


#Test functions
psql -q -f tests/test_remove_nulls_in_array_klasse.sql
psql -q -f tests/test_common_types_cleable_casts.sql
psql -q -f tests/test_common_types_cleable_casts.sql
psql -q -f tests/test_as_search_match_array.sql
psql -q -f tests/test_as_search_ilike_array.sql
#Facet
psql -q -f tests/test_facet_db_schama.sql
psql -q -f tests/test_as_create_or_import_facet.sql
psql -q -f tests/test_as_list_facet.sql
psql -q -f tests/test_as_read_facet.sql
psql -q -f tests/test_as_search_facet.sql
psql -q -f tests/test_as_update_facet.sql
psql -q -f tests/test_as_filter_unauth_facet.sql
#Klasse (BUT testing template-generated code through klasse, IM)
psql -q -f tests/test_as_update_klasse.sql
psql -q -f tests/test_as_read_klasse.sql
psql -q -f tests/test_as_list_klasse.sql
psql -q -f tests/test_as_search_klasse.sql
psql -q -f tests/test_remove_nulls_in_array_klasse.sql

#itsystem
psql -q -f tests/test_as_search_itsystem.sql
#sag
psql -q -f tests/test_as_create_or_import_sag.sql
psql -q -f tests/test_as_update_sag.sql
psql -q -f tests/test_as_search_sag.sql
psql -q -f tests/test_json_object_delete_keys.sql
psql -q -f tests/test_json_cast_function.sql
#dokument
psql -q -f tests/test_as_create_or_import_dokument.sql
psql -q -f tests/test_as_list_dokument.sql
psql -q -f tests/test_as_update_dokument.sql
psql -q -f tests/test_as_search_dokument.sql
#tilstand
psql -q -f tests/test_as_create_or_import_tilstand.sql
psql -q -f tests/test_as_update_tilstand.sql
psql -q -f tests/test_as_search_tilstand.sql
#indsats
psql -q -f tests/test_as_create_or_import_indsats.sql
psql -q -f tests/test_as_update_indsats.sql
psql -q -f tests/test_as_search_indsats.sql
psql -q -f tests/test_as_filter_unauth_indsats.sql
#aktivitet
psql -q -f tests/test_as_create_or_import_aktivitet.sql
psql -q -f tests/test_as_update_aktivitet.sql
psql -q -f tests/test_as_search_aktivitet.sql
