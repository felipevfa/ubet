server:
	python manage.py runserver 0.0.0.0:8000
test:
	python manage.py test
clean:
	find . -name '*.pyc' -type f -delete
	rm ubet/migrations/*
local:
	python manage.py runserver
migrations:
	python manage.py makemigrations ubet
	python manage.py migrate 
	python manage.py loaddata settings.json
shell:
	python manage.py shell
messages:
	django-admin makemessages -a
translations:
	django-admin compilemessages
