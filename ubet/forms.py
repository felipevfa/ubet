#coding: utf-8
from django import forms
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from ubet.models import Group,Ubet_user
from django.contrib.auth.models import User, UserManager
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime

my_default_errors = {
			'required' : 'Campo obrigatório.',
			'invalid' : 'Insira um valor válido.',
}

def validate_maioridade(arg):
	now = datetime.datetime.now()
	now = datetime.date(now.year,now.month,now.day)
	year = (now-arg)/365
	if year.days < 18:
		raise ValidationError( _('Apenas usuarios acima de 18 anos podem participar'), params={'year': year})


class UserSignupForm(UserCreationForm):
	# photo = forms.FileField(label="Avatar", required=False)
	nascimento = forms.DateField(required=True,validators=[validate_maioridade])
	nomec = forms.CharField(label = 'Nome completo',max_length=100)
	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2", 'first_name',)
		labels = { 'username': 'Nome de Usuário',
				   'email' : 'E-mail',	
				   'first_name' : 'Nome Público',
		}
		help_texts = {
			'username' : '',
		}

	def __init__(self, *args, **kwargs):
		super(UserSignupForm, self).__init__(*args, **kwargs)
		self.fields['username'].error_messages = my_default_errors
		self.fields['email'].error_messages = my_default_errors
		self.fields['password1'].label = "Senha"
		self.fields['password1'].error_messages = my_default_errors
		self.fields['password2'].label = "Confirme sua senha"
		self.fields['password2'].error_messages = my_default_errors
		self.fields['password2'].help_text = ''
		self.fields['nascimento'].label = "Data de Nascimento"
		self.fields['nascimento'].error_messages = my_default_errors
		self.fields['nomec'].error_messages = my_default_errors


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

class newgroupForm(forms.Form):
	"""docstring for newgroupForm"""

	position = forms.IntegerField(label = 'Em que numero voce apostara')

	class Meta:
		model = Group	
		fields = {'name', 'max_size','bet_value'}
		labels = {
			'name' : 'Nome do Grupo',
			'max_size' : 'Quantidade de membros',
			'bet_value' : 'Valor da Aposta',
		}		
	def check_values(self):
		tamanho = self.cleaned_data['max_size']
		posicao = self.cleaned_data['position']
		bet_value = self.cleaned_data['bet_value']
		errors = {
			'bet_error' : False,
			'size_error' : False,
			'position_error' : False,
		}
		if position < 1 or position > tamanho:
			errors['position_error']  = True

		if tamanho <= 1 or tamanho > 10:
			errors['size_error'] = True
		
		if bet_value < 1:
			errors['bet_value'] = True

		return errors

	def save(self,criador_id,commit=True):
		g = Group(
			creator = criador_id,
			name = self.cleaned_data['name'],
			max_size = self.cleaned_data['max_size'],
			bet_value = self.cleaned_data['bet_value'],
			cur_size = 1,
			)
		g.users
		if commit:
			g.save()
		return g