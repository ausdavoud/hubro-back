Backend for Hubro (Django 5 / Postgresql 16)
===
This project uses `uv` as its package manager. Refer to [this link](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) to install uv.

1. Create a virtual environment
```sh
uv venv
```

2. Install the dependencies
```sh
uv sync
```

3. Create a .env file in the same hierarchy as pyproject.toml
```sh
touch .env
```

4. Populate .env file according to .env_sample file

5. Change directory to hubro_back
```sh
cd hubro_back
```
6. If using NeonDB, set `CONN_MAX_AGE` to 0 in settings.py. 
NeonDB, due to its serverless nature, shuts down old connections. By setting 
CONN_MAX_AGE to 0 we tell django to close database connection after each request
to prevent using old connections closed by NeonDB.
```py
CONN_MAX_AGE = 0
```

7. Make migrations and migrate
```sh
python manage.py makemigrations && \
python manage.py migrate
```

8. Change cors headers urls in settings.py to the path url is running on
``` 
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    # Your paths here...
]
```
9.  Run the server
```sh
python manage.py runserver
````
