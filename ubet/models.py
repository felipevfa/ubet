# coding: utf-8
from django.db.models import F
from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth.models import User,BaseUserManager, AbstractBaseUser
from random import choice
import datetime
from django.utils import timezone
from django.db import IntegrityError

class Admin_settings(models.Model):
	"""Configuracoes gerais do servico. Para melhor desempenho, precisam ser armazenadas em cache"""

	time_to_expire = models.IntegerField(default=30)
	"""tempo de duracao maxima de um grupo"""

	group_max_capacity = models.IntegerField(default=10)
	win_tax = models.FloatField(default=0.04)
	"""um valor entre 0 e 1 que representa o percentual de comissao sobre o premio
	 do vencedor"""


class Ubet_user(models.Model):
	""" Classe que faz ligacao com classe User do django. 
	user.first_name eh na verdade o nome completo"""

	""" ligacao do Ubet_user com User"""
	django_user = models.OneToOneField(User,
		on_delete = models.CASCADE)

	date_of_birth = models.DateField()
	creditos = models.FloatField(default=100)
	
	def __unicode__(self):
		return 'ubet_user: ' +  str(self.django_user)
			
	def create_group(self,name,bet_value,max_size):
		g = Group(
			creator = self.django_user,
			name = name,
			bet_value = bet_value,
			max_size = max_size,
			)
		
		g.save()
		# g.add_user(self.django_user,position)
		
		return g

	def bet(self, group,position):
		""" levanta excecao se alguma condicao for quebrada durante o processo
		tenha em mente que uma aposta pode estar autorizada no inicio da chamada mas
		nao mais no fim da chamada da funcao

		retorna sucess,reason, onde
		sucess: true/false, se a aposta foi concluida com sucesso ou nao
		reason: motivo pelo qual a aposta nao ocorreu, ou \"\" caso contrario """
		success,reason = group.possible_bet(self.django_user)
		if success:
			try:
				group.add_user(self.django_user,position)
				self.creditos -= group.bet_value
				self.save()
				self.django_user.save()
				return True,''
			except:
				raise
		return False,reason


	
class Group(models.Model):
	"""Um grupo e uma coleção na qual ocorrem as apostas."""

	status_list = (('END','FINISHED'),('ABORT','CANCELED'),('WAIT','WAITING'))
	"""
	Grupo finalizado: O grupo tem a maxima quantidade de usuarios e o sorteio foi realizado
	Grupo abortado: O grupo nao atingiu a maxima quantidade de usuarios antes do prazo de tempo e foi
	cancelado
	Grupo em espera: O grupo esta ativo e esperando usuarios
	 """

	creator = models.ForeignKey(User,null=True,on_delete=models.SET_NULL,related_name='group_creator_user')
	""" por conta dos testes, um grupo pode ficar sem criador.
		Como um criador nao possui papel central na aposta, essa caracteristica
		foi mantida. """
	winner = models.ForeignKey(User,null=True,on_delete=models.SET_NULL,related_name='group_winner_user')
	name = models.CharField(max_length=50)

	max_size = models.IntegerField()
	"""quantidade maxima de usuarios no grupo"""

	bet_value = models.IntegerField()
	"""valor que se paga para entrar no grupo"""

	date_of_birth = models.DateTimeField(auto_now = True)
	date_of_death = models.DateTimeField(null=True)

	status = models.CharField(choices=status_list,default='WAITING',max_length=50)
	users = models.ManyToManyField(User,symmetrical=True,through='Group_link')

	def __unicode__(self):
		return self.name

	def update(self):
		"""
		O metodo update e chamado no grupo sempre que se deseja atualiza-lo 
		para verificar se o grupo atingiu a idade maxima ou numero maximo de membros.
		Se o grupo ficar cheio, um usuario dentro dele e sorteado para ser o vencedor, e o
		premio lhe e dado. 
		Se o grupo ficar velho, os creditos sao extornados aos usuarios

		"""
	
		sets = Admin_settings.objects.get(id=1)
		expire = sets.time_to_expire
		desconto = sets.win_tax
		now = timezone.now()
		if self.status == "WAITING":
			if  (now - self.date_of_birth).seconds / 60 >= expire or self.users.count() == self.max_size:
				if self.users.count() == self.max_size:
					self.status =  'FINISHED'
					self.date_of_death = timezone.now()
					self.winner = choice(self.users.all())	
					k = 1
					if self.max_size > 2:
						k = k - desconto
					self.winner.ubet_user.creditos += self.users.count()*self.bet_value*k
					self.winner.ubet_user.save()
				else:
					self.status = 'CANCELED'
					self.date_of_death = timezone.now()
					
					for user in self.users.all():
						user.ubet_user.creditos += self.bet_value
						user.ubet_user.save()
						user.save()
				for u in self.users.all():
					a = Notification(group = self,user=u)
					a.save()
				self.save()
	def time_left(self):
		"""retorna o tempo restante do grupo em minutos."""
		expire = Admin_settings.objects.get(id=1).time_to_expire
		if self.status == 'WAITING':
			now = timezone.now()
			active = (now - self.date_of_birth).seconds / 60
			return expire-active
		return 0

	def get_prize(self):
		"""retorna o valor do prêmio."""
		return self.bet_value*self.max_size;

	@staticmethod
	def active_groups(user,waiting=False):
		"""Mostra os grupos ativos para um usuario. 
		Por padrao, mostra apenas os que ele nao esta incluso. 
		Se waiting for True, retorna apenas os que ele esta incluso. """
		glist = Group.objects.filter(status='WAITING')
		for g in glist:
			g.update()
		if waiting:
			return glist.filter(status='WAITING').filter(group_link__user=user)
		else:
			return glist.filter(status='WAITING').exclude(group_link__user=user)


	@staticmethod	
	def total_active_groups():
		"""Mostra todos os grupos que estao ativos no momento"""
		glist = Group.objects.filter(status='WAITING')
		for g in glist:
			g.update()
		return glist

	def add_user(self,user,position):
		""" adiciona o usuario no grupo numa determinada posicao. Nao confundir com bet()"""
		gp = Group_link(user=user,group=self,position=position)

		try:
			# self.save()
			gp.save()
		except:
			raise
		
	def available_positions(self):
		"""retorna uma lista com os indices (comecando de 1) de quais posicoes estao abertas
		para aposta no grupo."""
		usuarios= Group.users_by_group(self)[0]
		user_positions = [Group_link.objects.get(user=u,group=self).position for u in usuarios]
		posicoes = range(1,self.max_size+1)
		for i in user_positions:
			posicoes.remove(i)
		return posicoes


	def users_by_group(self):
		"""retorna uma tupla com duas listas: a primeira componente possui uma lista 
		com os usuarios daquele grupo. A segunda componente e uma lista com as posicoes ocupadas 
		pelos usuarios (comecando de 1). O isemo usuario na lista user_list esta na posicao
		determinada pelo isemo elemento em position_list"""
		user_list = self.users.all()
		position_list = [Group_link.objects.get(user=u,group=self).position for u in user_list]
		return user_list,position_list

	def nicks_by_group(self):
		"""Retorna uma lista com os usernames dos usuarios participantes do grupo"""
		user_list = self.users.all()
		position_list = [Group_link.objects.get(user=u,group=self).position for u in user_list]
		return [u.username for u in user_list],position_list


	def cur_size(self):
		"""numero de usuarios presentes no grupo"""
		return self.users.count()

	@staticmethod
	def groups_by_user(user):
		""" retorna uma lista com os grupos aos quais o usuario faz parte"""
		glist = Group.objects.filter(users=user)
		for g in glist:
			g.update()
		return glist
	
	

	def possible_bet(self,user):
		"""retorna uma tupla: possible,reason
		Se possible for True, reason e uma string vazia.
		Caso contrario, reason contem uma string com justificativa de falha"""
		self.update()
		possible = True
		reason = ""
		if self.status != "WAITING":
			possible = False
			reason = _("Inactive Group")
			return possible,reason
		if self.cur_size() >= self.max_size:
			possible = False
			reason = _("Full Group")
			return possible,reason
		if user.ubet_user.creditos < self.bet_value:
			possible = False
			reason = _("Not enough credits")
			return possible,reason
		if user in self.users_by_group()[0]:
			possible = False
			reason = _("You've already betted in this group")
			return possible,reason
		
		if not user.is_active:
			possible = False
			reason = _("Offline User")
			return possible,reason
		return possible,reason

	def sim_list(self):
		"""retorna uma lista simulada do grupo.
		Uma lista simulada e uma lista de tamanho igual ao numero maximo de usuarios do grupo.
		Se x e y sao usuarios nas posicoes 2  e 4 de um grupo de tamanho 5, entao o metodo retornara
		a seguinte lista:
		[None,x,None,y,None]
		 . 
		"""
		l = [None]*self.max_size
		for u,p in zip(self.users_by_group()[0],self.users_by_group()[1]):
			l[p-1] = u
		return l

class Group_link(models.Model):
	"""um link descreve as participacoes de usuarios em um grupo. Nao é possivel ter
	dois usuarios numa mesma posicao, nem um mesmo usuario em duas posicoes no mesmo grupo.
	Essa classe representa o agregamento em SQL, e portanto so existe para representar 
	um banco relacional"""
	class Meta:
		unique_together = (	( "group",'position'),('user','group'))
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	group = models.ForeignKey(Group,on_delete = models.CASCADE)
	position = models.IntegerField()
	creation_time = models.DateTimeField(auto_now=True)
	
class Notification(models.Model):
	"""Uma notificacao e uma classe que representa que ha um aviso para o usuario de que
	um dos grupos dos quais ele participa mudou de status. A linha correspondente na tabela
	deve ser apagada quando o usuario visualizar a notificacao"""
	group = models.ForeignKey(Group,on_delete=models.CASCADE)
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	