#!/bin/bash

# Copy session pooler strong from supabase
PGPASSWORD="<password>"
CONNECTION_STRING="postgresql://postgres.<project-ref>:$PGPASSWORD@<pooler-host>:5432/postgres"
psql $CONNECTION_STRING -c "drop schema public cascade;"

rm */migrations/00*.py
python manage.py makemigrations
python manage.py migrate
python manage.py suppliers
python manage.py financial_accounts
python manage.py superusers