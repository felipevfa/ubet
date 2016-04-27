# coding: utf-8
import datetime,string
from random import choice,randint,sample
from ubet.models import User,Ubet_user,Group,Group_link
adj = ("grande", "bom", "novo", "pequeno", "próprio", "velho", "cheio", "branco", "longo", "único", "alto", "certo", "só", "possível", "claro", "capaz", "estranho", "negro", "enorme", "escuro", "seguinte", "mau", "diferente", "preciso", "difícil", "antigo", "bonito", "simples", "forte", "pobre", "sério", "belo", "feliz", "junto", "vermelho", "humano", "inteiro", "triste", "importante", "meio", "sentado", "fácil", "verdadeiro", "frio", "vazio", "baixo", "terrível", "próximo", "livre", "profundo", "jovem", "preto", "impossível", "vivo", "largo", "nu", "necessário", "azul", "natural", "quente", "completo", "verde", "pesado", "inglês", "especial", "rápido", "igual", "comprido", "principal")
nomes = ("Aarão", "Abdias", "Abel", "Abelâmio", "Abner", "Abelardo", "Abílio", "Abraão", "Abraim", "Abrão", "Absalão", "Abssilão", "Acácio", "Acilino", "Acílio", "Acúrsio", "Adail", "Adalberto", "Adalsindo", "Adalsino", "Adamantino", "Adamastor", "Adão", "Adauto", "Adauto", "Adelindo", "Adelmiro", "Adelmo", "Ademar", "Ademir", "Adeodato", "Aderico", "Adério", "Adérito", "Adiel", "Adílio", "Adner", "Adolfo", "Adonai", "Adonias", "Adónias", "Adonilo", "Adónis", "Adorino", "Adosindo", "Adriano", "Adrião", "Adriel", "Adrualdo", "Adruzilo", "Afonsino", "Afonso", "Afonso", "Afrânio", "Afre", "Africano", "Agapito", "Agenor", "Agnelo", "Agostinho", "Aguinaldo", "Aidé", "Aires", "Airton", "Aitor", "Aladino", "Alamiro", "Alan", "Alano", "Alão", "Alarico", "Albano", "Alberico", "Albertino", "Alberto", "Alcibíades", "Alcides", "Alcindo", "Alcino", "Aldaír", "Aldemar", "Alder", "Aldo", "Aldónio")
gnames = ("Shadowhand Knights", "SYR", "Blood Omnia", "The Evil Lords", "Pinky of the Charmed Shadows", "Angels of Blood Red Maner", "Mustache Knights", "Lions of D Haran Fis", "Warlock Forever", "Hells Valorous", "Your Hot List", "Everlasting Saints", "The Wtfpwnd", "Lucky Brigade", "Basement Militia", "Reign of the Phantom Hoopty", "Warriors of Blood Knuckle Nighthaven", "Amber Point", "The Sniper", "Knights of Dark Warriors Legacy", "Order of Gard Aganst Wâtch", "IMPERFEKT", "CONFLUENCE", "Laguna Tribe", "The Black Moon Club", "The Sad Abh", "Mystical Horde", "The Fist of Fruglys Insanity", "Keepers of Black Ignites", "Dawn of the Oxbloods Clan", "Doom Legion")
def random_nome():
	return str(sample(adj,1)[0]) + ' ' + str(sample(nomes,1)[0])

def random_string(arg):
	return ''.join(sample(string.lowercase+string.digits,arg))

def random_user(uname=None,senha=None):
	x = Ubet_user()
	x.full_name = random_nome()
	x.date_of_birth = datetime.date(randint(1900,2000),randint(1,12),randint(1,28))
	email = random_string(7) + '@email.com'
	x.creditos = 20;
	if senha is None:
		password = random_string(10)
	else:
		password = senha
	if uname is None:
		uname = random_nome()
	username = uname
	first_name = sample(nomes,1)
	x.django_user = User.objects.create_user(username,
		email=email,
		password=password,
		first_name=first_name)
	x.save()
	return username,x.full_name,x.date_of_birth,email,password,first_name


def grupo_aleatorio(nome=None):
	if nome == None:
		nome = choice(gnames)
	x = Group()
	x.bet_value = 10
	x.max_size = 10
	x.cur_size = 0
	x.name = nome
	x.save() 
	return x.name	


def populate():
	username = random_user()[0]
	username2 = random_user()[0]
	username3 = random_user()[0]
	
	try:
		nome_do_grupo = grupo_aleatorio()
	except:
		pass
	try:
		nome_do_grupo2 = grupo_aleatorio()
	except:
		pass
	try:
		nome_do_grupo3 = grupo_aleatorio()
	except:
		pass
	try:
		nome_do_grupo4 = grupo_aleatorio()
	except:
		pass

	user = User.objects.get(username=username)
	user2 = User.objects.get(username=username2)
	user3 = User.objects.get(username=username3)

	try:
		meu_grupo = Group.objects.get(name=nome_do_grupo)
	except:
		pass
	try:
		meu_grupo2 = Group.objects.get(name=nome_do_grupo2)
	except:
		pass
	try:
		meu_grupo3 = Group.objects.get(name=nome_do_grupo3)
	except:
		pass
	try:
		meu_grupo4 = Group.objects.get(name=nome_do_grupo4)
	except:
		pass





	
	#####################################################################
	#	incluindo usuarios a grupos 								 	#
	#	g1 = {1,3}, g2 = {2}, g3 = {1,3}								#
	#####################################################################
	try:
		meu_grupo.add_user(user,9)
	except:
		pass	
	try:
		meu_grupo.add_user(user3,3)
	except:
		pass	
	try:
		meu_grupo2.add_user(user2,1)
	except:
		pass

	try:
		meu_grupo3.add_user(user3,1)
	except:
		pass	

	try:
		p = 'pikachu'
		p = random_user(uname=p,senha='senhaforte')[0]
		p = User.objects.get(username=p)
		meu_grupo.add_user(p,4)
		print 'pikachu dentro'
	except:
		print 'pikachu n incluso'
	
def test():
	print 'usuarios'
	print User.objects.all()
	print Group.objects.all()

populate()
test()