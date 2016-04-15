from django.test import TestCase
from django.contrib.auth import authenticate, login
# Create your tests here.
from random import sample,randint
import string
from .models import Ubet_user,User,Group
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
		###
		#	Cria usuario aleatorio e salva no banco
		###
	def random_user(self):
		x = Ubet_user()
		x.full_name = random_string(30)
		x.date_of_birth = datetime.date(randint(1900,2000),randint(1,12),randint(1,29))
		email = random_string(6) + '@' +random_string(6) + '.com'
		password = random_string(10)
		username = random_string(10)
		first_name = random_string(10)
		x.django_user = User.objects.create_user(username,
			email=email,
			password=password,
			first_name=first_name)
		x.save()
		return x.full_name,x.date_of_birth,email,password,username,first_name
	def grupo_aleatorio(self):
		x = Group()
		x.bet_value = 10
		x.max_size = 10
		x.cur_size = 0
		x.name = 'mamao'
		x.save() 
		return x.name	
	def test_usuario(self):

		full_name,date_of_birth,email,password,username,first_name = self.random_user()

		###
		#	verifica se as caracteristicas criadas foram encontradas no banco
		###
		
		django_user_retrieved = User.objects.get(username=username)

		self.assertNotEqual(None ,django_user_retrieved)
		self.assertEqual(username,Ubet_user.objects.get(date_of_birth=date_of_birth).django_user.username)
		self.assertEqual(date_of_birth,User.objects.get(username=username).ubet_user.date_of_birth)
		self.assertEqual(full_name,django_user_retrieved.ubet_user.full_name)
		self.assertEqual(email,django_user_retrieved.email)
		self.assertEqual(first_name,django_user_retrieved.first_name)
		self.assertEqual(email,django_user_retrieved.email)
		self.assertEqual(django_user_retrieved.ubet_user.creditos,0)
		
		###
		#	tenta logar o usuario
		###
		

		try_login = authenticate(username=username,password=password)
		self.assertEqual(try_login.is_active,True)


	def test_grupos(self):
		full_name,date_of_birth,email,password,username,first_name = self.random_user()
		(,,,,username2,) = self.random_user()
		
		nome_do_grupo = self.grupo_aleatorio()
		user = User.objects.get(username=username)
		self.assertNotEqual(None,user)
		meu_grupo = Group.objects.get(name=nome_do_grupo)
		# n2 = self.grupo_aleatorio()
		self.assertNotEqual(None,meu_grupo)
		self.assertEqual(10,meu_grupo.bet_value)
		self.assertEqual(10,meu_grupo.max_size)
		meu_grupo.link.add(user)
		# print Group.objects.filter(link__username__startswith=username)
		self.assertEqual(User.objects.filter(group=meu_grupo)[0],user)
		self.assertEqual(Group.objects.filter(link__username__in=[username])[0],meu_grupo)

	def test_enderecos(self):
		###
		#	Verifica se os enderecos disponiveis estao dando certo
		###
		
		self.assertEqual(200,client.get('').status_code)
		self.assertEqual(200,client.get(reverse('signup')).status_code)
		self.assertEqual(200,client.get(reverse('login')).status_code)
		self.assertEqual(200,client.get(reverse('listall')).status_code)