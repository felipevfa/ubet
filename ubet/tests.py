from django.test import TestCase

# Create your tests here.
from random import sample,randint
import string
from ubet.models import User,ubet_user
import datetime
from django.test.utils import setup_test_environment
setup_test_environment()
from django.test import Client
from django.core.urlresolvers import reverse
def random_string(arg):
	return ''.join(random.sample(string.lowercase+string.digits,arg))

def  random_user():
	ubet_user = ubet_user()
	ubet_user.full_name = random_string(30)
	ubet_user.date_of_birth = datetime.date(randint(1900,2000),randint(1,13),randint(1,29))
	user = User()
	user.email = random_string(6) + '@' +random_string(6) + '.com'
	user.password = random_string(10)
	user.username = random_string(10)
	user.first_name = random_string(10)
	ubet_user.django_user = user
	ubet_user.save()
	user.save()


client = Client()
class testes(TestCase):
	def testesignup(self):
		d = {
			'teste' : 'camo'
		}
		response = client.get('/login/')
		print response