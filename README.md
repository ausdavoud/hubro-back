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

6. Make migrations and migrate
```sh
python manage.py makemigrations && \
python manage.py migrate
```

7. Run the server
```sh
python manage.py runserver
````