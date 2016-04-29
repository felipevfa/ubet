#coding: utf-8
from django import forms
from django.forms import ModelForm 
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from ubet.models import Group,Ubet_user
from django.contrib.auth.models import User, UserManager
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime
from rayquasa.settings import GROUP_MAX_CAPACITY as gmaxcap
import logging
my_default_errors = {
			'required' : 'Campo obrigatório.',
			'invalid' : 'Insira um valor válido.',
}

def validate_maioridade(arg):
	now = datetime.datetime.now()
	now = datetime.date(now.year,now.month,now.day)
	year = (now-arg)/365
	if year.days < 18:
		raise ValidationError( _('Only users above 18 can participate'),code='maioridade')


class UserSignupForm(UserCreationForm):
	nascimento = forms.DateField(required=True,label=_('Birthdate') ,help_text='xx/xx/xxxx')
	nascimento.validators=[validate_maioridade]
	# nascimento.widget	.attrs = {
	#     'class':'datepicker'
	# }
	nomec = forms.CharField(label = _('Full name'),max_length=100)
	class Meta:
		model = User
		fields = ("username", "email", 'first_name','password1','password2')
		labels = { 
				   'first_name' : _('Public Name'),
		}
		help_texts = {
			'username' : '',			
		}
	def __init__(self, *args, **kwargs):
		super(UserSignupForm, self).__init__(*args, **kwargs)
		self.fields['password2'].help_text = ''
		self.fields['username'].widget.attrs={
			'class': 'tooltipped',
			'data-tooltip' : _('The credential you use to log into the site')

		}
	def save(self, commit=True):
		user = User.objects.create_user(self.cleaned_data['username'],
			email = self.cleaned_data['email'],
			password = self.cleaned_data['password1'],
			first_name = self.cleaned_data['first_name'])
		uu = Ubet_user()
		uu.django_user = user
		uu.date_of_birth = self.cleaned_data['nascimento']
		uu.full_name = self.cleaned_data['nomec']
		if commit:
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
	
	class Meta:
		model = User
		fields = ('nome', 'password')
		labels = { 'username': _('Username'), 'password': _('Password') }

class new_group_Form(ModelForm):
	"""docstring for new_group_Form"""

	# position = forms.IntegerField(label = 'Em que numero voce apostara')
	
	class Meta:
		model = Group	
		fields = {'name', 'max_size','bet_value'}
		labels = {
			'name' : _('Group\'s name'),
			'max_size' : _('Number of members'),
			'bet_value' : _('Bet'),
		}
		


	def clean_bet_value(self):
		bet_value = self.cleaned_data['bet_value']
		if bet_value<1 :
			raise forms.ValidationError(_("The bet must have a positive value."),code='bet_value_er	')
		
		return bet_value
	def clean_max_size(self):
		max_size = self.cleaned_data['max_size']
		if max_size<=1 or max_size >  gmaxcap :
			raise forms.ValidationError(_("A group must have two members at least, and at most ")+ str(gmaxcap),code='max_size_tam')

		return max_size

	def save(self,criador,commit=True):

		#posicao = self.cleaned_data['position']
			
		return criador.ubet_user.create_group(name = self.cleaned_data['name'],
			bet_value = self.cleaned_data['bet_value'],
			max_size = self.cleaned_data['max_size'])
	