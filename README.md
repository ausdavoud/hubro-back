# Backend for Hubro (Django 5 / PostgreSQL 16)

## Backend

This project uses `uv` as its package manager. Refer to [this link](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) to install uv.

1. Create a virtual environment:

   ```sh
   uv venv
   ```

2. Install the dependencies:

   ```sh
   uv sync
   ```

3. Create a `.env` file in the same hierarchy as `pyproject.toml`:

   ```sh
   touch .env
   ```

4. Populate `.env` file according to `.env_sample` file.

5. Change directory to `hubro_back`:

   ```sh
   cd hubro_back
   ```

6. If using NeonDB, set `CONN_MAX_AGE` to 0 in `settings.py`. NeonDB, due to its serverless nature, shuts down old connections. By setting `CONN_MAX_AGE` to 0, we tell Django to close database connection after each request to prevent using old connections closed by NeonDB.

   ```python
   CONN_MAX_AGE = 0
   ```

7. Change CORS headers URLs in `settings.py` to the path URL is running on:

   ```python
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:8080",
       "http://127.0.0.1:8080",
       # Your paths here...
   ]
   ```

8. Run the following commands to setup the database:

   ```sh
   docker compose build
   docker compose up -d
   ```

   > Note: You can also access PgAmin at `127.0.0.1:5050` with:

   ```text
   username: root@root.com
   password: root
   ```

   and connect to database:

   ```text
   host: 192.168.0.2
   port: 5432
   database: hubro_db
   username: hubro_user
   password: hubro_password
   ```

9. Make migrations and migrate:

   ```sh
   python manage.py makemigrations \
   && python manage.py migrate \
   && python manage.py rd \
   && python manage.py financial_accounts
   ```

10. Run the server:

   ```sh
   python manage.py runserver
   ```

## Frontend Notes

> This project uses JWT authentication.

### Login (Getting `access token` and `refresh token`)

URL: `http://localhost:8000/token/`

Body:

```json
{
    "email": "d@g.com",
    "password": "dddddddd" // 8d
}
```

### Refresh token

URL: `http://localhost:8000/token/refresh`

Body

```json
{
    "refresh": "your refresh token"
}
```

### UUID for ws_connection

To be added...

## Reset DB

> CATION: USE THIS AT YOUR OWN RISK!

This project uses Docker Compose to run a sample PostgreSQL database.
You might occasionally need to reset the database. To do so, run `./reset_db.sh` script.

If running for the first time, you need to make it executable like so:

```sh
chmod +x reset_db.sh
```

Then run the script

```sh
./reset_db.sh
```

This will:

   1. Stop the running container.
   2. Drop the volume associated with the database
   3. Remove all migrations and create one from scratch.
   4. create a new database called `hubro_db` and run migrations.
   Additionally, it fills the database with sample data for R&D Static,
   Superuser, User, Instructor, Simulation Class, Team and Player tables.
