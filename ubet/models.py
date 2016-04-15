# coding: utf-8
from django.db import models
from django.contrib.auth.models import User,BaseUserManager, AbstractBaseUser
# class ubetUserManager(BaseUserManager):
# 	def create_user(self, username, email, password):
# 		if not username:
# 			raise ValueError("Defina um nome de usuário.")
#
# 		if not email:
# 			raise ValueError("Forneça um e-mail válido.")
#
# 		if not password or len(password) < 6:
# 			raise ValueError("Por favor, insira uma senha entre 6 e 16 caracteres.")
#
# 		# if not photo:
# 		# 	user = self.model(nick=username,
# 		# 				  	  identifier=self.normalize_email(email),
# 		# 				 	 )
# 		# else:
# 		# 	user = self.model(nick=username,
# 		# 					  identifier=self.normalize_email(email),
# 		# 					  photo=photo
# 		# 					 )
#
# 		user.set_password(password)
# 		user.save(using=self._db)
# 		return user
#
# 	def create_superuser(self, username, email, password, photo):
# 		if not username:
# 			raise ValueError("Defina um nome de usuário.")
#
# 		if not email:
# 			raise ValueError("Forneça um e-mail válido.")
#
# 		if not password or len(password) < 6:
# 			raise ValueError("Por favor, insira uma senha entre 6 e 16 caracteres.")
#
# 		# if not photo:
# 		# 	user = self.model(identifier=username,
# 		# 				  	  email=self.normalize_email(email),
# 		# 				 	 )
# 		# else:
# 		# 	user = self.model(identifier=username,
# 		# 					  email=self.normalize_email(email),
# 		# 					  photo=photo
# 		# 					 )
#
# 		user.is_admin = True
# 		user.set_password(password)
# 		user.save(using=self._db)
# 		return user

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
		


class Group(models.Model):
	"""Um grupo é uma coleção na qual ocorrem as apostas.
	Possui um numero maximo de membros, o numero atual de membros, um valor de aposta, e
	data_inicio sendo um datetime indicando quando o primeiro membro entrou no grupo.
	"""

	status_list = (('END','FINISHED'),('ABORT','CANCELED'),('WAIT','WAITING'))
	creator = models.ForeignKey(User,null=True,on_delete=models.SET_NULL,related_name='group_creator_user')
	winner = models.ForeignKey(User,null=True,on_delete=models.SET_NULL,related_name='group_winner_user')
	name = models.CharField(max_length=50)
	cur_size = models.IntegerField()
	max_size = models.IntegerField()
	bet_value = models.IntegerField()
	date_of_birth = models.DateTimeField(auto_now = True)
	status = models.CharField(choices=status_list,default='WAITING',max_length=50)
	group_user = models.ManyToManyField(User,symmetrical=True,through='Group_link')

class Group_link(models.Model):
	"""uma relacao descreve o conjunto de elementos de um grupo."""
	class Meta:
		unique_together = (	( "group",'position'),('user','group'))
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	group = models.ForeignKey(Group,on_delete = models.CASCADE)
	position = models.IntegerField()
	creation_time = models.DateTimeField(auto_now=True)


# class divida(models.Model):
# 	devedor = models.ForeignKey('ubetUser', on_delete = models.CASCADE)
# 	cobrador = models.ForeignKey('ubetUser', on_delete = models.CASCADE)
# 	valor = models.IntegerField()
	