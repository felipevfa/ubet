#coding: utf-8
from django import forms
from django.forms import ModelForm 
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
		raise ValidationError( _('Only users above 18 can participate'), params={'year': year},code='invalid')


class UserSignupForm(UserCreationForm):
	nascimento = forms.DateField(required=True,validators=[validate_maioridade],widget=forms.DateInput(attrs=
                                {
                                    'class':'datepicker'
                                }),
                                label=_('Birthdate'),
                                
                                
	)

	nascimento.input_type = 'date'
	nomec = forms.CharField(label = _('Full name'),max_length=100)
	class Meta:
		model = User
		fields = ("username", "email", 'first_name',)
		labels = { 
				   'first_name' : _('Public Name'),
				   
		}
		help_texts = {
			'username' : '',			
		}
	# nascimento.widget.attrs = {'type' : 'date'}


	def __init__(self, *args, **kwargs):
		super(UserSignupForm, self).__init__(*args, **kwargs)
		self.fields['password2'].help_text = ''

	# 	for f in  self.visible_fields():
	# 		print f
		

	def save(self, commit=True):
		user = User.objects.create_user(self.cleaned_data['username'],
			email = self.cleaned_data['email'],
			password = self.cleaned_data['password1'],
			first_name = self.cleaned_data['first_name'])
		uu = Ubet_user()
		uu.django_user = user
		uu.date_of_birth = self.cleaned_data['nascimento']
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
	"""docstring for newgroupForm"""

	# position = forms.IntegerField(label = 'Em que numero voce apostara')
	
	class Meta:
		model = Group	
		fields = {'name', 'max_size','bet_value'}
		labels = {
			'name' : _('Group\'s name'),
			'max_size' : _('Number of members'),
			'bet_value' : _('Bet'),
		}		
	def __init__(self, *args, **kwargs):
		super(ModelForm, self).__init__(*args, **kwargs)
		#self.fields['position'].error_messages = my_default_errors
		# self.fields['max_size'].error_messages = my_default_errors
	# 	# self.fields['bet_value'].error_messages = my_default_errors

	# 	# self.fields['max_size'].help_text = "Valor maior que 1"
	# 	self.fields['position'].label = 

	# # 	# self.fields['password2'].error_messages = my_default_errors
	# # 	# self.fields['max_size'].help_text = 'Um valor maior que 1'
	
	# def clean_max_size(self):
	#	data = self.cleaned_data['max_size']
	#	if data < 2 or  data > 10:
	#		raise forms.ValidationError('Valor invalido de tamanho do grupo!')
	#	return data

	# def clean_bet_value(self):
	#	data = self.cleaned_data['bet_value']
	#	if data < 1 :
	#		raise forms.ValidationError('Valor invalido de aposta!')
	#	return data
		
		# def clean_position(self):
		# 	data = self.cleaned_data['position']
		# 	if data < 1 or data > self.cleaned_data['max_size']:
		# 		raise forms.ValidationError("Valor invalido de posicao!")
		# 	return data


		# self.fields['max_size'].help_text = "Valor maior que 1"
		#self.fields['position'].label = "Em que posicao voce aposta (a partir de 1)"


	def check_values(self):
		tamanho = self.cleaned_data['max_size']
		# posicao = self.cleaned_data['position']
		bet_value = self.cleaned_data['bet_value']
		errors = {
			'bet_value_error' : False,
			'max_size_error' : False,
			#'position_error' : False,
		}
		# if posicao < 1 or posicao > tamanho:
			#errors['position_error']  = True

		if tamanho <= 1 or tamanho > 10:
			errors['max_size_error'] = True
		
		if bet_value < 1:
			errors['bet_value_error'] = True
		
		return errors

	def save(self,criador,commit=True):

		#posicao = self.cleaned_data['position']
			
		return criador.ubet_user.create_group(name = self.cleaned_data['name'],
			bet_value = self.cleaned_data['bet_value'],
			max_size = self.cleaned_data['max_size'])
	