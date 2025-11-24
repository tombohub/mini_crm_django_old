runserver:
	uv run ./manage.py runserver 5000

shell:
	uv run ./manage.py shell

makemigrations:
	uv run ./manage.py makemigrations

migrate:
	uv run ./manage.py migrate

reload:
	browser-sync 'http://127.0.0.1:5000' --files .

test:
	uv run pytest --reuse-db