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

class ubetUser(models.Model):


	usuario_django = models.OneToOneField(User,
		on_delete = models.CASCADE,
		primary_key = True)

	idade = models.IntegerField()
	def __str__(self):
		return usuario_django.__str__()
#
# class grupo(models.Model):
# 	"""Um grupo é uma coleção na qual ocorrem as apostas.
# 	Possui um numero maximo de membros, o numero atual de membros, um valor de aposta, e
# 	data_inicio sendo um datetime indicando quando o primeiro membro entrou no grupo.
# 	"""
# 	size = models.IntegerField()
# 	max_size = models.IntegerField()
# 	bet = models.IntegerField()
# 	data_inicio = models.DateTimeField(auto_now = True)
#
# class relacao(models.Model):
# 	"""uma relacao descreve o conjunto de elementos de um grupo."""
# 	usuario = models.ForeignKey('grupo', on_delete = models.CASCADE)
# 	grupo = models.ForeignKey('ubetUser',on_delete = models.CASCADE)
#
# class divida(models.Model):
# 	devedor = models.ForeignKey('ubetUser', on_delete = models.CASCADE)
# 	cobrador = models.ForeignKey('ubetUser', on_delete = models.CASCADE)
# 	valor = models.IntegerField()
