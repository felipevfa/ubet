from django.test import TestCase

# Create your tests here.
from random import sample,randint
import string
from .models import ubet_user,User
import	 datetime
from django.utils import timezone
from django.test.utils import setup_test_environment
setup_test_environment()
from django.test import Client
from django.core.urlresolvers import reverse
def random_string(arg):
	return ''.join(sample(string.lowercase+string.digits,arg))

client = Client()
class testes(TestCase):
	def testaendereco(self):
		x = ubet_user()
		x.full_name = random_string(30)
		db = x.date_of_birth = datetime.date(randint(1900,2000),randint(1,12),randint(1,29))
		user = User()
		email = random_string(6) + '@' +random_string(6) + '.com'
		password = random_string(10)
		username = user.username = random_string(10)
		first_name = random_string(10)
		x.django_user = User.objects.create_user(username,
			email=email,
			password=password,
			first_name=first_name)
		x.save()
		self.assertEqual(200,client.get('').status_code)
		self.assertEqual(200,client.get(reverse('signup')).status_code)
		self.assertEqual(200,client.get(reverse('login')).status_code)
		self.assertEqual(200,client.get(reverse('listall')).status_code)

		self.assertNotEqual(None ,User.objects.get(username=username))
		self.assertEqual(username,ubet_user.objects.get(date_of_birth=db).django_user.username)
		self.assertEqual(db,User.objects.get(username=username).ubet_user.date_of_birth)

