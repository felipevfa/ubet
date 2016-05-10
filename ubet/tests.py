# coding: utf-8
import rayquasa.settings
from django.test import TransactionTestCase
from django.contrib.auth import authenticate, login
# Create your tests here.
from ubet.forms import UserSignupForm,new_group_Form
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
import pytz
from django.utils import translation
from django.utils.translation import ugettext as _

def random_string(arg):
	return ''.join(sample(string.lowercase+string.digits,arg))


def random_user(username=None,creditos=None,dt=None):
		
		x = Ubet_user()
		if creditos is None:
			creditos = 100
		x.creditos = creditos
		if dt is None:
			dt = datetime.date(randint(1900,2000),randint(1,12),randint(1,28))
		x.date_of_birth = dt
		
		email = random_string(6) + '@' +random_string(6) + '.com'
		password = "senhaforte"
		if username is None:
			username = random_string(5)
		username = username
		first_name = random_string(10)
		u = User.objects.create_user(username,
			email=email,
			password=password,
			first_name=first_name,
		)
		u.ubet_user = x
		x.save()
		u.save()
		return u 
def random_group(nome=None,bet_value=10,max_size=10):
	if nome is None:
		nome = random_string(4)
	x = Group()
	x.bet_value = bet_value
	x.max_size = max_size
	x.name = nome
	x.save() 
	return x
client = Client()
class testes(TransactionTestCase):
	fixtures = ['settings.json']
					
	def test_usuario(self):

		u = random_user()
		username = u.username
		date_of_birth = u.ubet_user.date_of_birth
		email = u.email
		first_name = u.first_name
		###
		#	verifica se as caracteristicas criadas foram encontradas no banco
		###
		
		django_user_retrieved = User.objects.get(username=username)

		self.assertNotEqual(None ,django_user_retrieved)
		self.assertEqual(username,Ubet_user.objects.get(date_of_birth=date_of_birth).django_user.username)
		self.assertEqual(date_of_birth,User.objects.get(username=username).ubet_user.date_of_birth)
		self.assertEqual(email,django_user_retrieved.email)
		self.assertEqual(first_name,django_user_retrieved.first_name)
		self.assertEqual(email,django_user_retrieved.email)
		# self.assertEqual(django_user_retrieved.ubet_user.creditos,0)
		
		###
		#	tenta logar o usuario
		###
		

		try_login = authenticate(username=username,password="senhaforte")
		self.assertEqual(try_login.is_active,True)

	def test_active_groups(self):
		user_list = [random_user() for i in range(7)]
		group_list = [random_group() for i in range(7)]
		canceledgroup = random_group()
		canceledgroup.status = 'CANCELED'
		canceledgroup.save()
		users = random.sample(user_list,3)
		gs = random.sample(group_list,3)
		links = zip(users,gs)
		for u,g in links:
			g.add_user(u,1)

		for u,g in links:
			self.assertTrue(not g in Group.active_groups(u))
			self.assertTrue( g in Group.active_groups(u,True))
			self.assertTrue(not canceledgroup in Group.active_groups(u))

	def test_grupos(self):

		#####################################################################
		#	gerando users e grupos aleatorios,							 	#
		#####################################################################
		username = random_user(username='username1').username
		username2 = random_user(username='username2').username
		username3 = random_user(username='username3').username
		
		nome_do_grupo = random_group(nome='nome_do_grupo1')
		nome_do_grupo2 = random_group(nome='nome_do_grupo2')
		nome_do_grupo3 = random_group(nome='nome_do_grupo3')
		nome_do_grupo4 = random_group(nome='nome_do_grupo4')
		
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

		self.assertTrue(meu_grupo in Group.total_active_groups() )
		self.assertTrue(meu_grupo2 in Group.total_active_groups())
				

		self.assertTrue(5 in meu_grupo.available_positions())
		self.assertFalse(9 in meu_grupo.available_positions())
		self.assertFalse(0 in meu_grupo.available_positions())
		self.assertFalse(-1 in meu_grupo.available_positions())
		self.assertFalse(meu_grupo.max_size+1 in meu_grupo.available_positions())


		#	testando se para quaisquer posicoes, a lista de disponiveis esta correta
		#	e se ele retorna corretamente como nao disponivel
		l = random.sample(range(1,10),5)
		x = []
		for i in l:
			usename = random_user().username
			user = User.objects.get(username=usename)
			x.append(user)
			meu_grupo4.add_user(user,i)
			self.assertTrue(meu_grupo4.cur_size() == len(x))
			self.assertFalse(i in meu_grupo4.available_positions())
		
		for i in l:
			usename = random_user().username
			self.assertRaises(Exception,meu_grupo4.add_user,(User.objects.get(username=usename),i))



		retorno_usuarios,posicoes = meu_grupo4.users_by_group()
		for u in x:
			self.assertTrue(u in retorno_usuarios)
		for u,p in zip(retorno_usuarios,posicoes):
			self.assertTrue(Group_link.objects.get(user=u,group=meu_grupo4).position == p)


		user_list = [ User.objects.get(username=random_user().username) for i in range(10) ]
		g = random_group()
		g = Group.objects.get(name=g)
		for u,i in zip(user_list,range(1,11)):
			g.add_user(u,i)
		self.assertRaises(Exception,g.add_user,(user_list[-1],4))

		

	def test_user_cp_view(self):
		"""verificando se a view user_cp gera o html com dados desejados"""
		u = random_user()
		c = Client()
		c.login(username=u.username,password='senhaforte')
		g = random_group()
		g.add_user(u,1)
		r = c.get(reverse('user_cp')).content
		self.assertTrue(u.first_name in r)
		self.assertTrue(str(u.email) in r)
		self.assertTrue( str(u.ubet_user.date_of_birth.day) in r)
		# self.assertTrue( str(u.ubet_user.date_of_birth.month) in r)
		self.assertTrue( str(u.ubet_user.date_of_birth.year) in r)
		self.assertTrue( str(u.date_joined.day) in r)
		# self.assertTrue( str(u.date_joined.month) in r)
		self.assertTrue( str(u.date_joined.year) in r)
		self.assertTrue( str(u.ubet_user.creditos) in r)
		self.assertTrue( str(u.first_name) in r)
		self.assertTrue( str(_('Full name') ) in r )
		self.assertTrue( str( _('E-mail')    ) in r )
		self.assertTrue( str(_('Birthdate') ) in r )
		self.assertTrue( str(_('Date Joined') ) in r )
		self.assertTrue( str(_('Credits') ) in r )
		self.assertTrue(g.name in r )


		g.delete()
	def test_view_signup_then_user_cp(self):
		"""na view: cadastra usuario e verifica se as informacoes estao no user_cp """
		password = random_string(8)
		form_data = {
			'username' : random_string(10),
			'email' : random_string(6)+'@mail.com',
			'first_name' : random_string(6),
			'password1' : password,
			'password2' : password,
			'nascimento' : '12/31/1800',
			}
		form = UserSignupForm(data=form_data)
		self.assertTrue(form.is_valid())
		r = self.client.post(reverse('signup'),form_data)
		# print r.context['form']
		self.assertTrue(r.status_code != 404)
		self.assertTrue(User.objects.count() > 0)
		u = User.objects.get(username=form_data['username'])
		self.client.login(username=form_data['username'],password=password)
		r = self.client.get(reverse('user_cp')).content
		self.assertTrue( form_data['email'] in r)
		self.assertTrue( form_data['first_name'] in r)
		self.assertTrue( form_data['nascimento'].split('/')[2] in r)

		# print r
		self.assertTrue(str(u.first_name) in r)
		# self.assertTrue(u.email.split('@')[0] in r)
		self.assertTrue( str(u.ubet_user.date_of_birth.day) in r)
		# self.assertTrue( str(u.ubet_user.date_of_birth.month) in r)
		self.assertTrue( str(u.ubet_user.date_of_birth.year) in r)
		self.assertTrue( str(u.date_joined.day) in r)
		# self.assertTrue( str(u.date_joined.month) in r)
		self.assertTrue( str(u.date_joined.year) in r)
		self.assertTrue( str(u.ubet_user.creditos) in r)

		self.assertTrue( str(u.first_name) in r)
		self.assertTrue( str(_('Full name') ) in r )
		self.assertTrue( str(_('E-mail') ) in r )
		self.assertTrue( str(_('Birthdate') ) in r )
		self.assertTrue( str(_('Date Joined') ) in r )
		self.assertTrue( str(_('Credits') ) in r )
		
	def test_new_group(self):
		cx = {
			'bet_value' : '10',
			'max_size' : 10,
			'name' : 'meugrupo',
		}
		u = random_user()
		self.client.login(username=u.username,password='senhaforte')
		r = self.client.post(reverse('new_group'),data=cx,follow=False)
		
		self.assertTrue(Group.objects.get(name=u.username+'_10'))
		self.assertTrue(len(Group.objects.all()) != 0)
	def test_new_group_bet_fail(self):
		cx = {
			'bet_value' : '-1',
			'max_size' : 10,
			'name' : 'meugrupo',
		}
		u = random_user()
		self.client.login(username=u.username,password='senhaforte')
		r = self.client.post(reverse('new_group'),data=cx,follow=False)
		self.assertTrue(len(Group.objects.all()) == 0)
	def test_new_group_size_fail(self):
		cx = {
			'bet_value' : '1',
			'max_size' : 1,
			'name' : 'meugrupo',
		}
		u = random_user()
		self.client.login(username=u.username,password='senhaforte')
		r = self.client.post(reverse('new_group'),data=cx,follow=False)
		self.assertTrue(len(Group.objects.all()) == 0)
	def test_aposta_finished(self):
		""" enche manualmente usuarios em um grupo e testa se encerra corretamente"""
		apostadores = 10
		user_list = [random_user(creditos=100) for i in range(apostadores)]

		g = random_group(max_size=apostadores,bet_value=1)

		for i,u in enumerate(user_list,1):
			self.client.login(username=u.username,password='senhaforte')
			cx = {
				'bet_position' : i
			}
			r = self.client.post(reverse('bet',args=[g.id]),cx)
			# print '>>>>>'
			self.assertTrue(u in Group.objects.get(id=g.id).users_by_group()[0])
		
		g.update()
		win = 0
		lose = 0
		for u in User.objects.all():
			if u.ubet_user.creditos == 99:
				lose += 1
			elif u.ubet_user.creditos > 100:
				win += 1
		self.assertEqual(lose,apostadores-1)
		self.assertEqual(win,1)
		self.assertEqual(g.cur_size(),apostadores)
		self.assertEqual(g.status,"FINISHED")
	
	def test_aposta_canceled(self):
		fixture = ['settings.json']
		c= Client()
		setup_test_environment()
		apostadores = 9
		user_list = [random_user(creditos=100) for i in range(apostadores)]
		g = random_group(max_size=apostadores+1,bet_value=1)
		self.assertTrue(c.get('').status_code != 404)
		for i,u in enumerate(user_list,1):
			c.login(username=u.username,password='senhaforte')
			# self.assertTrue(c.get(reverse('list_all_groups')).request['user'].is_active)
			cx = {
				'bet_position' : i
			}
			r = c.post(reverse('bet',args=[g.id]),cx)
			self.assertTrue(r.status_code != 404)
			# self.assertTrue(User.objects.get(id=u.id) in g.users_by_group())
		g.date_of_birth = datetime.datetime(1,1,1,tzinfo=pytz.utc)
		g.update()
		win = 0
		anomalia = 0
		lose = 0
		normal = 0
		for u in User.objects.all():
			if u.ubet_user.creditos == 99:
				lose += 1
			elif u.ubet_user.creditos == 100 + apostadores-1:
				win += 1
			elif u.ubet_user.creditos == 100 :
				normal += 1
			else:
				anomalia += 1
		self.assertEqual(g.status,"CANCELED")
		self.assertEqual(lose,0)
		self.assertEqual(win,0)
		self.assertEqual(anomalia,0)
		self.assertEqual(normal,apostadores)

		self.assertEqual(g.cur_size(),apostadores)

	password = random_string(8)
	form_data = {'username' : random_string(10),
			'email' : random_string(6)+'@mail.com',
			'first_name' : random_string(6),
			'password1' : password,
			'password2' : password,
			'nascimento' : datetime.date(randint(1,10),randint(1,10),randint(1,10)),
			'nomec' : random_string(10)
			}
	def test_signupform_view_dataen(self):
		"""verificando se a view aceita data em ingles qnd o idioma eh ingles"""
		c = Client()
		r = c.get(reverse('signup'))
		r = c.get(reverse('signup'))
		self.assertTrue(r.status_code!=404)
		data = self.form_data
		data['username'] = 'lordpikachu'
		data['nascimento'] = '12/31/1990'
		
		c.post(reverse('signup'),data=self.form_data)
		self.assertTrue(User.objects.get(username='lordpikachu').username == 'lordpikachu')

	def test_signupform_view_datapt(self):
		"""verificando se a view aceita data em portugues qnd o idioma eh portugues"""
		
		c = Client()
		r = c.get(reverse('signup'))
		r = c.get(reverse('signup'))
		self.assertTrue(r.status_code!=404)
		data = self.form_data
		data['username'] = 'lordpikachu2'
		data['nascimento'] = '31/12/1990'
		translation.activate('pt-br')
		r = c.post(reverse('signup'),data=self.form_data)

		# form = r.context['form']
		self.assertTrue(User.objects.get(username='lordpikachu2').username == 'lordpikachu2')
		translation.activate('en')
	def test_signupform_valido(self):
		"""verificando se o form eh valido para dados validos"""
		form = UserSignupForm(data=self.form_data)
		self.assertTrue(form.is_valid())
	def test_signup_form_invalido_muitonovo(self):
		password = random_string(8)
		form_data = {'username' : random_string(10),
			'email' : random_string(6)+'@mail.com',
			'first_name' : random_string(6),
			'password1' : password,
			'password2' : password,
			'nascimento' : datetime.date(datetime.datetime.now().year,randint(1,10),randint(1,10)),
			'nomec' : random_string(10)
			}
		form = UserSignupForm(data=form_data)
		self.assertTrue(_("Only users above 18 can participate") in form.errors['nascimento'] )
	
	def test_signup_form_invalido_muitonovo_view(self):
		c = Client()
		password = random_string(8)
		form_data = {'username' : random_string(10),
			'email' : random_string(6)+'@mail.com',
			'first_name' : random_string(6),
			'password1' : password,
			'password2' : password,
			'nascimento' : datetime.date(datetime.datetime.now().year,randint(1,10),randint(1,10)),
			'nomec' : random_string(10)
			}
		c.get('')
		r = c.post(reverse('signup'),data=form_data)
		self.assertTrue(r.status_code != 404)
		form = r.context['form']
		self.assertTrue(_("Only users above 18 can participate") in form.errors['nascimento']  )

	def test_signup_form_invalido_campovazio(self):
		password = random_string(8)
		form_data = {
			'username' : random_string(10),
			'email' : random_string(6)+'@mail.com',
			'first_name' : random_string(6),
			'password1' : '',
			'password2' : password,
			'nascimento' : datetime.date(randint(1,10),randint(1,10),randint(1,10)),
			'nomec' : random_string(10)
			}
		form = UserSignupForm(data=form_data)
		self.assertFalse(form.is_valid())

	def test_signupform_valido_data_en(self):
		password = random_string(8)
		form_data = {'username' : random_string(10),
			'email' : random_string(6)+'@mail.com',
			'first_name' : random_string(6),
			'password1' : password,
			'password2' : password,
			'nascimento' : '12/31/1800',
			'nomec' : random_string(10)
			}
		form = UserSignupForm(data=form_data)
		self.assertTrue(form.is_valid())
	

	def test_new_group_form_vazio(self):
		form_data = {
			'bet_value' : '',
			'max_size' : '',
			'name' : '',
			}
		form = new_group_Form(data=form_data)
		self.assertFalse(form.is_valid())		
	def test_new_group_form_valido(self):
		form_data = {
			'bet_value' : '1',
			'max_size' : '2',
			'name' : 'mamao',
			}
		form = new_group_Form(data=form_data)
		self.assertTrue(form.is_valid())		

	def test_new_group_form_doubleerro(self):
		form_data = {
			'bet_value' : '-1',
			'max_size' : '200',
			'name' : 'mamao',
			}
		form = new_group_Form(data=form_data)
		self.assertTrue(len(form.errors['max_size'])>0)
		self.assertTrue(len(form.errors['bet_value'])>0)

		self.assertFalse(form.is_valid())		

	def test_new_group_form_erro_bet(self):
		form_data = {
			'bet_value' : '200',
			'max_size' : '-1',
			'name' : 'mamao',
			}
		form = new_group_Form(data=form_data)
		self.assertTrue(len(form.errors['max_size'])>0)

		self.assertFalse(form.is_valid())		

	def test_new_group_form_erro_bet_view(self):
		form_data = {
			'bet_value' : '200',
			'max_size' : '2',
			'name' : 'mamao',
			}
		c = Client()
		u = random_user(username='pikachu')
		c.login(username='pikachu',password='senhaforte')
		r = c.get(reverse('new_group'))
		r = c.get(reverse('new_group'))
		self.assertTrue(r.status_code != 404)
		
		r = c.post(reverse('new_group'),data=form_data,follow=True)
		self.assertTrue(r.status_code != 404)
		
		self.assertTrue(len(Group.objects.all())>0)		
	def test_new_group_form_erro_duploerro_view(self):
		form_data = {
			'bet_value' : '-1',
			'max_size' : '-1',
			'name' : 'mamao',
			}
		c = Client()
		u = random_user(username='pikachu')
		c.login(username='pikachu',password='senhaforte')
		r = c.get(reverse('new_group'))
		r = c.get(reverse('new_group'))
		self.assertTrue(r.status_code != 404)
		
		r = c.post(reverse('new_group'),data=form_data,follow=True)
		self.assertTrue(r.status_code != 404)
		
		self.assertTrue(len(Group.objects.all())==0)			


	def test_sim_list(self):
		"""verifica se as posicoes da sim list estao corretas"""
		apostadores = 5
		posicoes = sample(range(1,10),apostadores)
		user_list = [random_user() for i in range(5)]
		g = random_group(max_size=10,bet_value=1)
		for u,p in zip(user_list,posicoes):
			g.add_user(u,p)
		simlist = g.sim_list()

		for p,u in zip(posicoes,user_list):
			self.assertTrue(simlist[p-1] == u)
		for i in range(1,10):
			if i not in posicoes:
				self.assertTrue(simlist[i-1] is None)


	def test_list_waiting_view(self):
		u = random_user(username="user",creditos=100)
		gl = [random_group() for i in range(10)]

		self.client.login(username=u.username,password='senhaforte')
		r = self.client.get(reverse('list_waiting'))
		for g in gl:
			self.assertTrue(g.name in r.content)
		for g in gl[0:4]:
			g.add_user(u,1)
		r = self.client.get(reverse('list_waiting'))
		for g in gl[0:4]:
			self.assertTrue(not g.name in r.content)
		for g in gl[5:]:
			self.assertTrue(g.name in r.content)
			
		#	nao eh pq ele cria o grupo que esta apostando
		self.assertEqual(100,User.objects.get(username="user").ubet_user.creditos)
