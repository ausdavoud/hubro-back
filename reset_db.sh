#!/bin/bash

# Remove db files
docker compose down
docker volume rm hubro-back_db_psql
rm */migrations/00*.py

# Create migrations
python manage.py makemigrations 

# Run docker and wait for db initialization
docker compose up --remove-orphans -d
sleep 2

# Run prepopulation command 
python manage.py migrate
python manage.py rd
python manage.py financial_accounts
python manage.py superuser

docker compose down