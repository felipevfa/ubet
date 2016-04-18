import datetime,string
from random import choice,randint,sample
from ubet.models import User,Ubet_user,Group,Group_link

def random_string(arg):
	return ''.join(sample(string.lowercase+string.digits,arg))
def random_user(uname=None):
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


def grupo_aleatorio(nome=None):
	if nome == None:
		nome = random_string(5)
	x = Group()
	x.bet_value = 10
	x.max_size = 10
	x.cur_size = 0
	x.name = nome
	x.save() 
	return x.name	


def populate():
	username,full_name,date_of_birth,email,password,first_name = random_user(uname='Jean Wyllys')
	username2 = random_user(uname='Bolsonaro')[0]
	username3 = random_user(uname='Ze maria')[0]
	
	nome_do_grupo = grupo_aleatorio(nome='PT')
	nome_do_grupo2 = grupo_aleatorio(nome='PSDB')
	nome_do_grupo3 = grupo_aleatorio(nome='Rede')
	nome_do_grupo4 = grupo_aleatorio(nome='League of tretas')
	
	user = User.objects.get(username=username)
	user2 = User.objects.get(username=username2)
	user3 = User.objects.get(username=username3)

	meu_grupo = Group.objects.get(name=nome_do_grupo)
	meu_grupo2 = Group.objects.get(name=nome_do_grupo2)
	meu_grupo3 = Group.objects.get(name=nome_do_grupo3)
	meu_grupo4 = Group.objects.get(name=nome_do_grupo4)


	
	#####################################################################
	#	incluindo usuarios a grupos 								 	#
	#	g1 = {1,3}, g2 = {2}, g3 = {1,3}								#
	#####################################################################

	link = Group_link(user=user,group = meu_grupo,position=9)
	try:
		link.save()
	except:
		print user.username + ' ' + meu_grupo.name + ' conflito'
	link = Group_link(user=user,group = meu_grupo3,position=1)
	try:
		link.save()
	except:
		print user.username + ' ' + meu_grupo.name + ' conflito'
	
	link = Group_link(user=user2,group=meu_grupo2,position=2)
	try:
		link.save()
	except:
		print user.username + ' ' + meu_grupo.name + ' conflito'
	
	link = Group_link(user=user3,group=meu_grupo3,position=3)
	try:
		link.save()
	except:
		print user.username + ' ' + meu_grupo.name + ' conflito'
	
	
	link = Group_link(user=user3,group=meu_grupo,position=3)
	try:
		link.save()
	except:
		print user.username + ' ' + meu_grupo.name + ' conflito'
	
def test():
	print 'usuarios'
	print User.objects.all()
	g = Group.objects.get(name='PT')
	print Group.users_by_group(g)