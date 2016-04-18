from django.test import TransactionTestCase
from django.contrib.auth import authenticate, login
# Create your tests here.
from ubet.forms import UserSignupForm
from random import sample,randint
import string,random
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
	def random_user(self,uname=None):
		
		x = Ubet_user()
		x.full_name = random_string(30)
		x.date_of_birth = datetime.date(randint(1900,2000),randint(1,12),randint(1,28))
		email = random_string(6) + '@' +random_string(6) + '.com'
		password = random_string(10)
		if uname is None:
			uname = random_string(5)
		username = uname
		first_name = random_string(10)
		x.django_user = User.objects.create_user(username,
			email=email,
			password=password,
			first_name=first_name)
		x.save()
		return username,x.full_name,x.date_of_birth,email,password,first_name
	def grupo_aleatorio(self,nome=random_string(4)):
		x = Group()
		x.bet_value = 10
		x.max_size = 10
		x.cur_size = 0
		x.name = nome
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
		username,full_name,date_of_birth,email,password,first_name = self.random_user(uname='username1')
		username2 = self.random_user(uname='username2')[0]
		username3 = self.random_user(uname='username3')[0]
		
		nome_do_grupo = self.grupo_aleatorio(nome='nome_do_grupo1')
		nome_do_grupo2 = self.grupo_aleatorio(nome='nome_do_grupo2')
		nome_do_grupo3 = self.grupo_aleatorio(nome='nome_do_grupo3')
		nome_do_grupo4 = self.grupo_aleatorio(nome='nome_do_grupo4')
		
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
		#	incluindo usuarios a grupos 								 	#
		#	g1 = {1,3}, g2 = {2}, g3 = {1,3}								#
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

		self.assertTrue(user in list(User.objects.filter(group=meu_grupo3)) )
		self.assertTrue(user2 in list(User.objects.filter(group=meu_grupo2)) )
		self.assertTrue(user3 in list(User.objects.filter(group=meu_grupo3)) )
		self.assertTrue(user2 in list(User.objects.filter(group=meu_grupo2)) )
		self.assertTrue(user2 in list(User.objects.filter(group=meu_grupo2)) )
		self.assertFalse(user3 in list(User.objects.filter(group=meu_grupo2)) )
		self.assertFalse(user in list(User.objects.filter(group=meu_grupo4)) )

		self.assertEqual(Group_link.objects.get(group=meu_grupo,user=user).position , 9)

		# g = Group.objects.all()[0]
		
		# for i in Group.users_by_group(meu_grupo):
				# print i.username
		
		self.assertTrue(meu_grupo in Group.groups_by_user(user))
		self.assertFalse(meu_grupo2 in Group.groups_by_user(user))
		self.assertTrue(meu_grupo3 in Group.groups_by_user(user))

		self.assertTrue(meu_grupo in Group.active_groups() )
		self.assertTrue(meu_grupo2 in Group.active_groups())
				
		self.assertTrue(5 in meu_grupo.available_positions())
		self.assertFalse(9 in meu_grupo.available_positions())
		self.assertFalse(0 in meu_grupo.available_positions())
		self.assertFalse(-1 in meu_grupo.available_positions())
		self.assertFalse(meu_grupo.max_size+1 in meu_grupo.available_positions())

		l = random.sample(range(1,10),5)
		for i in l:
			usename = self.random_user()[0]
			meu_grupo4.add_user(User.objects.get(username=usename),i)
			self.assertFalse(i in meu_grupo4.available_positions())
		
		for i in l:
			usename = self.random_user()[0]
			self.assertRaises(Exception,meu_grupo4.add_user,(User.objects.get(username=usename),i))

		ul = [ User.objects.get(username=self.random_user()[0]) for i in range(11) ]
		g = Group(name=random_string(5))
		for i in range(1,11):
			g.add_user(ul[i-1],i)
		self.assertRaises(Exception,g.add_user,(ul[-1],4))


	def test_enderecos(self):
		###
		#	Verifica se os enderecos disponiveis estao dando certo.
		#	Alguns enderecos devem ser encontrados apenas por usuarios, mas agora nao esta assim.
		##
		
		self.assertEqual(200,client.get('').status_code)
		self.assertEqual(200,client.get(reverse('signup')).status_code)
		self.assertEqual(200,client.get(reverse('login')).status_code)
		self.assertEqual(200,client.get(reverse('list_all_users')).status_code)
		self.assertEqual(200,client.get(reverse('list_all_groups')).status_code)

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

