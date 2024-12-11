# read Host IP address from .env file in the current directory
set -o allexport
source .env
set +o allexport

# Replace with the directory where your docker-compose.yml is located on the server
APP_DIR="/app" 
VOLUME_NAME="app_db_psql"

# Shut down the container and remove the volume, then recreate the container
ssh root@$PGHOST "cd $APP_DIR && docker compose down && docker volume rm $VOLUME_NAME"
rm */migrations/00*.py
ssh root@$PGHOST "cd $APP_DIR && docker compose up --remove-orphans -d"

# Wait for the container to start up and then run the migrations
sleep 5
python manage.py makemigrations
python manage.py migrate
python manage.py rd
python manage.py financial_accounts
python manage.py superuser