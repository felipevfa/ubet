release: python manage.py makemigrations ubet
	     python manage.py migrate 
	     python manage.py loaddata settings.json
         python povoar.py
web: gunicorn rayquasa.wsgi --log-file -
