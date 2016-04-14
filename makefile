clean:
	find . -name '*.pyc' -type f -delete
local:
	python manage.py runserver
migration:
	python manage.py makemigrations ubet
migrate:
	python manage.py migrate
shell:
	python manage.py shell
