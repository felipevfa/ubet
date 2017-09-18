release: python manage.py makemigrations ubet
	     python manage.py migrate 
	     python manage.py loaddata settings.json
web: gunicorn rayquasa.wsgi --log-file -
