rm -f db.sqlite3
rm -f simulation/migrations/00*.py

python manage.py makemigrations
python manage.py migrate