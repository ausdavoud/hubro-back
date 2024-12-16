#!/bin/bash

# Create a .env file and put PGHOST and PGPASSWORD in it
set -o allexport
source .env
set +o allexport


# Copy session pooler strong from supabase
CONNECTION_STRING="postgresql://$PGUSER:$PGPASSWORD@$PGHOST:5432/postgres"
SQL_COMMAND="
DO \$\$ 
BEGIN 
    EXECUTE (
        SELECT string_agg(
            format('DROP TABLE IF EXISTS public.%I CASCADE;', tablename), ' '
        ) 
        FROM pg_tables 
        WHERE schemaname = 'public'
    );
END 
\$\$;
"
psql $CONNECTION_STRING -c "$SQL_COMMAND"

rm */migrations/00*.py
python manage.py makemigrations
python manage.py migrate
python manage.py suppliers
python manage.py financial_accounts
python manage.py superusers