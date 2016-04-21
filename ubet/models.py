# coding: utf-8
from django.db import models
from django.contrib.auth.models import User,BaseUserManager, AbstractBaseUser
from random import choice
from django.db import IntegrityError

class Ubet_user(models.Model):
	django_user = models.OneToOneField(User,
		on_delete = models.CASCADE)
	full_name = models.CharField(max_length=100)
	date_of_birth = models.DateField()
	creditos = models.FloatField(default=0)
	def __unicode__(self):
		return self.django_user.username+'\n'+ \
			self.django_user.first_name+'\n'+ \
			self.django_user.password+'\n'+\
			self.django_user.email+'\n'+\
			str(self.django_user.date_joined)+'\n'+\
			self.full_name+'\n'+\
			str(self.date_of_birth)+'\n'+\
			str(self.creditos)
			
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

	def bet(self, value):
		newValue = (self.creditos - value)

		if newValue >= 0:
			self.creditos = newValue

			try:
				self.save()
			except:
				raise
			
			return True

		return False

	
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
	status = models.CharField(choices=status_list,default='WAITING',max_length=50)
	users = models.ManyToManyField(User,symmetrical=True,through='Group_link')

	def __unicode__(self):
		return self.name
	def update(self):
		now = datetime.datime.now()
		for i in Group.objects.all():
			if (now - i.date_of_birth).minute >= 30:
				if i.user.count() == i.max_size:
					i.status =  'FINISHED'
					i.winner = choice(i.users.all()).pid
				else:
					i.status = 'CANCELED'
	
	def add_user(self,user,position):
		gp = Group_link(user=user,group=self,position=position)

		try:
			# self.save()
			gp.save()
			success = True
		except:
			success = False
		
		return success

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

	def cur_size(self):
		return self.users.count()
	@staticmethod
	def groups_by_user(user):
		return Group.objects.filter(users=user)
	
	@staticmethod
	def active_groups():
		return Group.objects.filter(status='WAITING')

class Group_link(models.Model):
	"""uma relacao descreve o conjunto de elementos de um grupo. Nao é possivel ter
	dois usuarios numa mesma posicao, nem um mesmo usuario em duas posicoes."""
	class Meta:
		unique_together = (	( "group",'position'),('user','group'))
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	group = models.ForeignKey(Group,on_delete = models.CASCADE)
	position = models.IntegerField()
	creation_time = models.DateTimeField(auto_now=True)
