
# coding: utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ubet.forms import UserSignupForm, UserAuthenticationForm,new_group_Form
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from ubet.models import Ubet_user,User,Group
from django.contrib import messages

# Create your views here.
def list_all_groups(request):
	groups = Group.active_groups();

	users_by_group = {}

	for g in groups:
		g.user_list = list(Group.users_by_group(g))

	return render(request,'ubet/list_all_groups.html', {'grupos': groups })

def new_group(request):
	error_msg = ''

	if request.method == 'POST':
		form = new_group_Form(request.POST, request.FILES)
		has_db_errors = False

		if form.is_valid():
			errors = form.check_values()

			if errors['position_error']:
				error_msg = error_msg + 'Posicao invalida.<br>'
				has_db_errors = True

			if errors['max_size_error']:
				error_msg = error_msg + 'Tamanho invalido.<br>'
				has_db_errors = True

			if errors['bet_value_error']:
				error_msg = error_msg + 'Valor de aposta invalido.<br>'
				has_db_errors = True


			if has_db_errors:
				return render(request, 'ubet/new_group.html', { 'form': form, 'new_groups_msg': error_msg })
			else:
				form.save(request.user)
				
				return HttpResponseRedirect(reverse('list_all_groups'))
	else:
		form = new_group_Form()

	return render(request, 'ubet/new_group.html', {'form': form })

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
				return render(request, 'ubet/signup.html', { 'form': form,  })
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
				msg = "Olá, {}".format(user.username)
				return HttpResponseRedirect(reverse(list_all_groups))

				login(request, user)
				msg = "Olá, {}".format(user.username)
				return HttpResponseRedirect(reverse(list_all_groups))
			else:
				return render(request, 'ubet/login.html', { 'toast': 'Conta desativada.', 'form': form })
		else:
			return render(request, 'ubet/login.html', { 'toast': 'Combinação de usuário e senha incorreta.', 'form': form })
	else:
		return render(request, 'ubet/login.html', { 'form': form })

def list_all_users(request):
	return render(request,'ubet/list_all_users.html',{'li':Ubet_user.objects.all()})

def logout(request):
	# logger.debug('logout')
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
		return render(request, 'ubet/user_cp.html', { 'user': request.user, 'user_groups': Group.groups_by_user(request.user) })
	else:
		form = UserAuthenticationForm()
		return render(request, 'ubet/login.html', { 'login_msg': 'Você precisa estar logado para acessar essa página.',
												 'form': form })

def group_info(request):
	if 'g_id' in request.GET:
		try:
			g = Group.objects.get(id=request.GET['g_id'])
		except ObjectDoesNotExist:
			return render(request, 'ubet/group_info.html', { 'error_msg': 'Desculpe, não encontramos informações desse grupo.', 'p_title': 'Erro' })			

		u = g.users_by_group()
		user_list = u[0]
		position_list = u[1]

		return render(request, 'ubet/group_info.html', {'group': g, 'users': zip(user_list, position_list), 'p_title': g.name })
	
	return render(request, 'ubet/group_info.html', { 'error_msg': 'Desculpe, ocorreu um erro.', 'p_title': 'Erro'})

	#else:
	#	form = UserAuthenticationForm()
	#	return render(request, reverse('login'), { 'login_msg': 'Você precisa conectar-se para ver os grupos.',
	#												'form': form })


