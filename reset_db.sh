#!/bin/bash

# Remove db files
docker compose down
docker volume rm hubro-back_db_psql
rm -f simulation/migrations/00*.py

# Create migrations
python manage.py makemigrations 

# Run docker and wait for db initialization
docker compose up --remove-orphans -d
sleep 3

# Run prepopulation command 
python manage.py migrate
python manage.py rd
python manage.py financial_accounts
python manage.py seed

docker compose down