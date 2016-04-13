#coding: utf-8
from django import forms
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from ubet.models import ubetUser


class UserSignupForm(UserCreationForm):
	# photo = forms.FileField(label="Avatar", required=False)

	class Meta:
		model = ubetUser
		fields = ("nome", "nome_completo","identifier", "password1", "password2",)
		labels = { 'nome': 'nome de usuario', 
				   'nome_completo': 'nomecompleto',
				   'identifier' : 'email',
				 }

	def save(self, commit=True):
		user = super(UserCreationForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		user.nick = self.cleaned_data["nome"]
		
		#if self.photo:
		#	user.photo = self.cleaned_data["photo"]

		if commit:
			user.save()

		return user

	def check_values(self):
		nome = self.cleaned_data["nome"]
		email = self.cleaned_data["identifier"]
		errors = { 'user_error': False,
		           'email_error': False 
		         }

		try:
			if (ubetUser.objects.get(nome=nome)):
				errors['user_error'] = True
		except ubetUser.DoesNotExist:
			errors['user_error'] = False

		try:
			if (ubetUser.objects.get(identifier=email)):
				errors['email_error'] = True
		except ubetUser.DoesNotExist:
			errors['email_error'] = False

		return errors;

class UserAuthenticationForm(AuthenticationForm):
	username = forms.CharField(label='Nome de Usuário', max_length=20)
	password = forms.CharField(label='Senha', widget=forms.PasswordInput)

	class Meta:
		model = ubetUser
		fields = ('nome', 'password')
		labels = { 'username': 'Nome de Usuário', 'password': 'Senha' }

	

