
# coding: utf-8
from django.db.models import F

from django.db import models
from django.contrib.auth.models import User,BaseUserManager, AbstractBaseUser
from random import choice
import datetime
from django.utils import timezone
from django.db import IntegrityError
from rayquasa.settings import TIME_TO_EXPIRE as expire 
class Ubet_user(models.Model):
	# ligacao com User do django. user.first_name eh o nome completo

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
	"""Um grupo é uma coleção na qual ocorrem as apostas.
	Possui um numero maximo de membros, o numero atual de membros, um valor de aposta, e
	data_inicio sendo um datetime indicando quando o primeiro membro entrou no grupo.
	"""

	status_list = (('END','FINISHED'),('ABORT','CANCELED'),('WAIT','WAITING'))
	creator = models.ForeignKey(User,null=True,on_delete=models.SET_NULL,related_name='group_creator_user')
	winner = models.ForeignKey(User,null=True,on_delete=models.SET_NULL,related_name='group_winner_user')
	name = models.CharField(max_length=50)
	max_size = models.IntegerField()
	bet_value = models.IntegerField()
	date_of_birth = models.DateTimeField(auto_now = True)
	date_of_death = models.DateTimeField(null=True)

	status = models.CharField(choices=status_list,default='WAITING',max_length=50)
	users = models.ManyToManyField(User,symmetrical=True,through='Group_link')

	def __unicode__(self):
		return self.name

	def update(self):
		now = timezone.now()
		if self.status == "WAITING":
			if  (now - self.date_of_birth).seconds / 60 >= expire or self.users.count() == self.max_size:
				if self.users.count() == self.max_size:
					self.status =  'FINISHED'
					self.date_of_death = timezone.now()
					self.winner = choice(self.users.all())	
					self.winner.ubet_user.creditos += self.users.count()*self.bet_value
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
		if self.status == 'WAITING':
			now = timezone.now()
			active = (now - self.date_of_birth).seconds / 60
			return expire-active
		return 0

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
		glist = Group.objects.filter(status='WAITING')
		for g in glist:
			g.update()
		return glist

	def add_user(self,user,position):
		gp = Group_link(user=user,group=self,position=position)

		try:
			# self.save()
			gp.save()
		except:
			raise
		
	def available_positions(self):
		usuarios= Group.users_by_group(self)[0]
		user_positions = [Group_link.objects.get(user=u,group=self).position for u in usuarios]
		posicoes = range(1,self.max_size+1)
		for i in user_positions:
			posicoes.remove(i)
		return posicoes


	def users_by_group(self):
		user_list = self.users.all()
		position_list = [Group_link.objects.get(user=u,group=self).position for u in user_list]
		return user_list,position_list

	def nicks_by_group(self):
		user_list = self.users.all()
		position_list = [Group_link.objects.get(user=u,group=self).position for u in user_list]
		return [u.username for u in user_list],position_list


	def cur_size(self):
		return self.users.count()

	@staticmethod
	def groups_by_user(user):
		glist = Group.objects.filter(users=user)
		for g in glist:
			g.update()
		return glist
	
	

	def possible_bet(self,user):
		self.update()
		possible = True
		reason = ""
		if self.status != "WAITING":
			possible = False
			reason = "Grupo Inativo"
			return possible,reason
		if self.cur_size() >= self.max_size:
			possible = False
			reason = "Grupo Cheio"
			return possible,reason
		if user.ubet_user.creditos < self.bet_value:
			possible = False
			reason = "Creditos Insuficientes"
			return possible,reason
		if not user.is_active:
			possible = False
			reason = "Usuario Offline"
			return possible,reason
		return possible,reason

	def sim_list(self):
		l = [None]*self.max_size
		for u,p in zip(self.users_by_group()[0],self.users_by_group()[1]):
			l[p-1] = u
		return l
class Group_link(models.Model):
	"""uma relacao descreve o conjunto de elementos de um grupo. Nao é possivel ter
	dois usuarios numa mesma posicao, nem um mesmo usuario em duas posicoes."""
	class Meta:
		unique_together = (	( "group",'position'),('user','group'))
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	group = models.ForeignKey(Group,on_delete = models.CASCADE)
	position = models.IntegerField()
	creation_time = models.DateTimeField(auto_now=True)
	
class Notification(models.Model):
	group = models.ForeignKey(Group,on_delete=models.CASCADE)
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	