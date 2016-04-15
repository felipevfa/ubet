
# coding: utf-8


from django.shortcuts import render
from ubet.forms import UserSignupForm, UserAuthenticationForm
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from ubet.models import Ubet_user
# Create your views here.

def signup(request):
	# logger.debug('signup')
	error_msg = ''

	if request.method == 'POST':
		form = UserSignupForm(request.POST, request.FILES)
		has_db_errors = False

		if form.is_valid():
			errors = form.check_values()

			if errors['user_error']:
				error_msg = error_msg + 'Usuário já cadastrado.<br>'
				has_db_errors = True

			if errors['email_error']:
				error_msg = error_msg + 'E-mail já cadastrado.<br>'
				has_db_errors = True

			if has_db_errors:
				return render(request, 'ubet/signup.html', { 'form': form, 'signup_msg': error_msg })
			else:
				user = form.save()
				user.save()

				new_user = authenticate(username=request.POST['username'],
										password=request.POST['password1'])
				auth_login(request, new_user)

				return HttpResponseRedirect(reverse('user_cp'))
	else:
		form = UserSignupForm()

	return render(request, 'ubet/signup.html', {'form': form })



def login(request):
	form = UserAuthenticationForm()
	# logger.debug('login')

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']


		user = authenticate(username=username, password=password)

		if user is not None:
			if user.is_active:
				auth_login(request, user)
				return HttpResponseRedirect(reverse('user_cp'))

				login(request, user)
				return HttpResponseRedirect(reverse('user_cp'))
			else:
				return render(request, 'ubet/login.html', { 'login_msg': 'Conta desativada.', 'form': form })
		else:
			return render(request, 'ubet/login.html', { 'login_msg': 'Combinação de usuário e senha incorreta.', 'form': form })
	else:
		return render(request, 'ubet/login.html', { 'form': form })
def listall(request):
	return render(request,'ubet/listall.html',{'li':Ubet_user.objects.all()})


def logout(request):
	logger.debug('logout')
	auth_logout(request)
	return HttpResponseRedirect(reverse('login'))

def profile(request,username):
	user = lolzinUser.objects.get(nick=username)
	liga_str = user.league.split()[0]
	if liga_str == 'unranked':
		liga_img_index = 0
	else:
		liga_img_index = lollib.ligas.index(liga_str)+1
	contexto = {
		'profile_user' : user,
		'imgsrc_liga' : 'lolzin/img/rank'+str(liga_img_index)+'.png',
		'background' : lollib.profile_background[liga_str]
	}
	return render(request,'lolzin/profile.html', contexto)

def user_cp(request):
	if request.user.is_authenticated():
		return render(request, 'ubet/user_cp.html')
	else:
		form = UserAuthenticationForm()
		return render(request, 'ubet/login.html', { 'login_msg': 'Você precisa estar logado para acessar essa página.',
												 'form': form })
