test:
	python manage.py test
clean:
	find . -name '*.pyc' -type f -delete
local:
	python manage.py runserver
migrations:
	python manage.py makemigrations ubet
migrate:
	python manage.py migrate
shell:
	python manage.py shell
