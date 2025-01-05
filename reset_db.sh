#!/bin/bash

if [ "$1" == "-r" ]; then
  echo "Remigrating database..."
  rm */migrations/00*.py
  python manage.py makemigrations
  python manage.py dbshell -- -c "drop schema public cascade; create schema public;"
  python manage.py migrate
  echo "Database remigrated."
else
  echo "Flushing database..."
  python manage.py flush --no-input
  echo "Database flushed."
fi
python manage.py suppliers
python manage.py financial_accounts
python manage.py superusers