from django.test import TransactionTestCase
from django.contrib.auth import authenticate, login
# Create your tests here.
from ubet.forms import UserSignupForm
from random import sample,randint
import string
from .models import Ubet_user,User,Group,Group_link
import	 datetime
from django.utils import timezone
from django.test.utils import setup_test_environment
setup_test_environment()
from django.test import Client
from django.core.urlresolvers import reverse
from django.db import IntegrityError
def random_string(arg):
	return ''.join(sample(string.lowercase+string.digits,arg))



client = Client()
class testes(TransactionTestCase):
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
		return username,x.full_name,x.date_of_birth,email,password,first_name
	def grupo_aleatorio(self):
		x = Group()
		x.bet_value = 10
		x.max_size = 10
		x.cur_size = 0
		x.name = random_string(4)
		x.save() 
		return x.name	
	def test_usuario(self):

		username,full_name,date_of_birth,email,password,first_name = self.random_user()

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

		#####################################################################
		#	gerando users e grupos aleatorios,							 	#
		#####################################################################
		username,full_name,date_of_birth,email,password,first_name = self.random_user()
		username2 = self.random_user()[0]
		username3 = self.random_user()[0]
		
		nome_do_grupo = self.grupo_aleatorio()
		nome_do_grupo2 = self.grupo_aleatorio()
		nome_do_grupo3 = self.grupo_aleatorio()
		nome_do_grupo4 = self.grupo_aleatorio()
		
		user = User.objects.get(username=username)
		user2 = User.objects.get(username=username2)
		user3 = User.objects.get(username=username3)

		self.assertNotEqual(None,user)
		self.assertNotEqual(None,user2)
		self.assertNotEqual(None,user3)

		meu_grupo = Group.objects.get(name=nome_do_grupo)
		meu_grupo2 = Group.objects.get(name=nome_do_grupo2)
		meu_grupo3 = Group.objects.get(name=nome_do_grupo3)
		meu_grupo4 = Group.objects.get(name=nome_do_grupo4)


		self.assertNotEqual(None,meu_grupo)
		self.assertEqual(10,meu_grupo.bet_value)
		self.assertEqual(10,meu_grupo.max_size)
		self.assertEqual('WAITING',meu_grupo.status)
		# print Group.objects.filter(link__username__startswith=username)
		
		#####################################################################
		#	 incluindo usuarios a grupos 								 	#
		#####################################################################
		link11 = Group_link(user=user,group = meu_grupo,position=9)
		link11.save()
		
		link13 = Group_link(user=user,group = meu_grupo3,position=1)
		link13.save()

		link22 = Group_link(user=user2,group=meu_grupo2,position=2)
		link22.save()
		
		link33 = Group_link(user=user3,group=meu_grupo3,position=3)
		link33.save()

		
		link31 = Group_link(user=user3,group=meu_grupo,position=3)
		link31.save()
		#####	isso nao pode acontecer
		##
		#	
		#	dois caras numa mesma posicao
		link12 = Group_link(user=user,group=meu_grupo2,position=2)
		self.assertRaises(IntegrityError,link12.save)
		
		#	o mesmo cara no mesmo grupo numa posicao diferente
		link11 = Group_link(user=user,group=meu_grupo,position=10)
		self.assertRaises(IntegrityError,link11.save)
		#
		##
		###


		
		#####################################################################
		#	verificando se usuarios estao nos grupos e suas posicoes	 	#
		#####################################################################		
		self.assertEqual(user in list(User.objects.filter(group=meu_grupo)) , True)
		self.assertEqual(Group_link.objects.get(group=meu_grupo,user=user).position , 9)

		self.assertEqual(user in list(User.objects.filter(group=meu_grupo3)) , True)
		self.assertEqual(user2 in list(User.objects.filter(group=meu_grupo2)) , True)
		self.assertEqual(user3 in list(User.objects.filter(group=meu_grupo3)) , True)
		self.assertEqual(user2 in list(User.objects.filter(group=meu_grupo2)) , True)
		self.assertEqual(user3 in list(User.objects.filter(group=meu_grupo2)) , False)
		self.assertEqual(user2 in list(User.objects.filter(group=meu_grupo2)) , True)
		self.assertEqual(user in list(User.objects.filter(group=meu_grupo4)) , False)

		self.assertEqual(Group_link.objects.get(group=meu_grupo,user=user).position , 9)


		

		# self.assertEqual(Group.objects.filter(link__username__in=[username])[0],meu_grupo)

	def test_enderecos(self):
		###
		#	Verifica se os enderecos disponiveis estao dando certo
		###
		
		self.assertEqual(200,client.get('').status_code)
		self.assertEqual(200,client.get(reverse('signup')).status_code)
		self.assertEqual(200,client.get(reverse('login')).status_code)
		self.assertEqual(200,client.get(reverse('listall')).status_code)

	def test_signupform(self):
		password = random_string(8)
		form_data = {'username' : random_string(10),
			'email' : random_string(6)+'@mail.com',
			'first_name' : random_string(6),
			'password1' : password,
			'password2' : password,
			'nascimento' : datetime.date(randint(1,10),randint(1,10),randint(1,10)),
			'nomec' : random_string(10)
			}
		form = UserSignupForm(data=form_data)
		self.assertTrue(form.is_valid())

		password = random_string(8)
		form_data = {'username' : random_string(10),
			'email' : random_string(6)+'@mail.com',
			'first_name' : random_string(6),
			'password1' : password,
			'password2' : password,
			'nascimento' : datetime.date(2015,randint(1,10),randint(1,10)),
			'nomec' : random_string(10)
			}
		form = UserSignupForm(data=form_data)
		self.assertFalse(form.is_valid())

