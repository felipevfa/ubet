clean:
	find . -name '*.pyc' -type f -delete
local:
	python manage.py runserver
