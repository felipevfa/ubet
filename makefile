test:
	python manage.py test
clean:
	find . -name '*.pyc' -type f -delete
local:
	python manage.py runserver
migrations:
	python manage.py makemigrations ubet
	python manage.py migrate ubet
shell:
	python manage.py shell
