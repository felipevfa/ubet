#coding: utf-8
from django import forms
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from ubet.models import Ubet_user
from django.contrib.auth.models import User, UserManager

class UserSignupForm(UserCreationForm):
	# photo = forms.FileField(label="Avatar", required=False)
	nascimento = forms.DateField(required=True)
	nomec = forms.CharField(max_length=100)


	class Meta:
		model = User
		fields = ("username","email",'first_name', "password1", "password2",)
		labels = { 'username': 'Nome de Usuario',
				   'email' : 'e-mail',
				   'first_name' : 'Nome publico',
		}

	def save(self, commit=True):
#		user = super(UserCreationForm, self).save(commit=False)
		user = User.objects.create_user(self.cleaned_data['username'],
			email = self.cleaned_data['email'],
			password = self.cleaned_data['password1'],
			first_name = self.cleaned_data['first_name'])
#		.set_password(self.cleaned_data["password1"])
		uu = Ubet_user()
		uu.django_user = user
		uu.date_of_birth = self.cleaned_data['nascimento']

		# user.nick = self.cleaned_data["nome"]

		#if self.photo:
		#	user.photo = self.cleaned_data["photo"]

		if commit:
#			user.save()
			uu.save()

		return uu

	def check_values(self):
		nome = self.cleaned_data["username"]
		email = self.cleaned_data["email"]
		errors = { 'user_error': False,
		           'email_error': False
		         }

		try:
			if (User.objects.get(username=nome)):
				errors['user_error'] = True
		except User.DoesNotExist:
			errors['user_error'] = False

		try:
			if (User.objects.get(email=email)):
				errors['email_error'] = True
		except User.DoesNotExist:
			errors['email_error'] = False

		return errors;

class UserAuthenticationForm(AuthenticationForm):
	username = forms.CharField(label='Nome de Usuário', max_length=20)
	password = forms.CharField(label='Senha', widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ('nome', 'password')
		labels = { 'username': 'Nome de Usuário', 'password': 'Senha' }



