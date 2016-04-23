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
shell:
	python manage.py shell
transfile:
	django-admin makemessages -l en
translations:
	django-admin compilemessages
