
# coding: utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from ubet.forms import UserSignupForm, UserAuthenticationForm,new_group_Form
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from ubet.models import Ubet_user,User,Group,Notification

from rayquasa.settings import TIME_TO_EXPIRE as expire
from rayquasa.settings import GROUP_MAX_CAPACITY as gmaxcap


from django.contrib import messages
from django.template import RequestContext
import datetime,logging
from django.utils import timezone
# Create your views here.
from django.utils.translation import ugettext_lazy as _
logger = logging.getLogger(__name__)
@login_required()
def list_all_groups(request):
	groups = Group.active_groups();
	if Notification.objects.filter(user=request.user).count() > 0:
		messages.add_message(request, messages.INFO, 'Hello world.')
		print 'mamao'
		print Notification.objects.filter(user=request.user).count()
		print 'melao'
	logger.debug('list_all_groups')
	return render(request,'ubet/list_all_groups.html', {'grupos': groups })

@login_required()
def new_group(request):
	logger.debug('new_group')
	if request.method == 'POST':
		logger.debug('new_group post')
		form = new_group_Form(request.POST)
		if form.is_valid():
			logger.debug('new_group is valid')
			group = form.save(request.user)
			return HttpResponseRedirect(reverse(bet,args=[group.id]))
		else:
			logger.debug('new group not valid')
			return render(request, 'ubet/new_group.html', {'form': form })
	elif request.method == 'GET':
		logger.debug('new_group GET')
		form = new_group_Form()	
		return render(request, 'ubet/new_group.html', {'form': form })
	logger.debug('new_group limbo')

def signup(request):
	logger.debug('signup')
	error_msg = ''

	if request.method == 'POST':
		logger.debug('signup post')
		form = UserSignupForm(request.POST)
		if form.is_valid():
			user = form.save()
			user.save()

			new_user = authenticate(username=request.POST['username'],
									password=request.POST['password1'])
			auth_login(request, new_user)
			logger.debug('signup post OK')
			return HttpResponseRedirect(reverse('user_cp'))
		else:
			logger.debug('signup form no valid')
			return render(request,'ubet/signup.html',{'form' : form})
		
	elif request.method == 'GET':
		logger.debug('signup get')
		form = UserSignupForm()
		return render(request, 'ubet/signup.html', {'form': form })
	logger.debug('signup limbo')


def login(request):
	form = UserAuthenticationForm()
	logger.debug('login')

	msg = _('original')
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		logger.debug(username + 'logandoo')
		user = authenticate(username=username, password=password)

		if user is not None:
			if user.is_active:
				auth_login(request, user)
				msg = _('Hello, ')
				msg += "{}".format(user.username)
				# request.LANGUAGE_CODE = 'pt-br'
				return redirect(reverse('list_all_groups'))
			else:
				return render(request, 'ubet/login.html', { 'toast': _('Account disabled'), 'form': form })
		else:
			return render(request, 'ubet/login.html', { 'toast': _('Username and password do not match'), 'form': form })
	else:
		if request.user.is_active:
			return HttpResponseRedirect(reverse(list_all_groups))
		msg = _("Welcome")
		return render(request, 'ubet/login.html', { 'form': form ,'toast':msg})

@login_required()
def list_all_users(request):

	return render(request,'ubet/list_all_users.html', {'li':Ubet_user.objects.all()})

@login_required()
def logout(request):
	# logger.debug('logout')
	auth_logout(request)
	return HttpResponseRedirect(reverse('login'))


@login_required()
def user_cp(request):
	logger.debug('user_cp')
	user_groups = Group.groups_by_user(request.user)
			
	notificacoes =  Notification.objects.filter(user=request.user)
	if request.user.is_authenticated():
		contexto = {
			'user': request.user, 
			'user_groups': user_groups,
			'datejoined' : request.user.date_joined.date(),
			'notification' : notificacoes,
		}
		logger.debug('user' +str( request.user))
		logger.debug('user_groups' +str(  user_groups))
		logger.debug('datejoined' +str( request.user.date_joined.date()))
		logger.debug('notification' +str( notificacoes))

		return render(request, 'ubet/user_cp.html', contexto)
	else:
		form = UserAuthenticationForm()
		return render(request, 'ubet/login.html', { 'login_msg': _('Only logged users can access this page'),
												 'form': form })

@login_required()
def notification(request,group_id):
	logger.debug('notification')
	n = Notification.objects.get(id=group_id)
	g = n.group.id
	logger.debug(n)
	logger.debug(g)
	n.delete()

	return HttpResponseRedirect(reverse(group_info,args=[g]))

@login_required()	
def group_info(request,group_id):
	logger.debug('group_info ' + str(group_id))
	try:
		g = Group.objects.get(id=group_id)
		g.update()
		# g.sim_list()
	except ObjectDoesNotExist:
		logger.debug('group_info exception')
		return render(request, 'ubet/group_info.html', { 'error_msg': _('Sorry, this group does not exist.'), 'p_title': 'Erro' })			

	u = g.users_by_group()
	user_list = u[0]
	position_list = u[1]
	canBet = False
	warning = ""
	toast = "masqbelo toast"
	remaining = ''
	
	if g.status == 'WAITING':
		remaining =  expire - (timezone.now() - g.date_of_birth).seconds / 60
		if request.user in user_list:
			toast = _("You are in this group")
		else:
			toast = _("You are not in this group")
	elif g.status == "FINISHED":
		u = request.user
		if request.user in g.users_by_group()[0]:
			if request.user != g.winner:
				toast = _("You lost this bet")
			else:
				toast = _("You won this bet")
	elif g.status == "CANCELED":
		toast = _("Group canceled")

	if request.user in user_list:

		warning = _('You\'ve already betted in this group.')
	else:
		if request.user.ubet_user.creditos < g.bet_value:
			warning = _('Not enough credits.')
		else:
			canBet = True

	if g.status == "CANCELED":
		canBet = False
	sl = g.sim_list()
	contexto = {'group': g, 
		'users': zip(user_list, position_list), 
		'p_title': g.name, 
		'canBet': canBet, 
	 	'warning': warning ,
	 	'toast' : toast,
	 	'remaining' : remaining,
	 	'sim_list' : sl,
	}
	logger.debug('users' + str(contexto['users']))
	logger.debug('group' + str(contexto['group']))
	logger.debug('p_title' + str(contexto['p_title']))
	logger.debug('canBet' + str(contexto['canBet']))
	logger.debug('warning' + str(contexto['warning']))
	logger.debug('toast' + str(contexto['toast']))
	logger.debug('remaining' + str(contexto['remaining']))
	logger.debug('sim_list' + str(contexto['sim_list']))

	return render(request, 'ubet/group_info.html',contexto )


	#else:
	#	form = UserAuthenticationForm()
	#	return render(request, reverse('login'), { 'login_msg': 'Você precisa conectar-se para ver os grupos.',
	#												'form': form })

@login_required()
def bet(request,group_id):
	# Se há um novo grupo sendo criado, recupera ele através de Sessions.
	logger.debug('bet')
	if request.method == 'GET':
		logger.debug('bet get')	
		try:
			group = Group.objects.get(id=group_id)
		except ObjectDoesNotExist:
			logger.debug('bet exception')
			group = None
		# Verifica se o grupo foi encontrado.
		if group is not None:
			ul = group.publicnames_by_group()
			users = ul[0]
			positions = ul[1]
			user_list = zip(users, positions)		
			# 	# Verifica se o usuário tem mesmo créditos para apostar
			available = [None]*group.max_size

			for (u, p) in user_list:
				available[p-1] = u
			x = group.possible_bet(request.user)
			canBet = x[0]
			reason = x[1]
			contexto = {
				'group' : group,
				'available' : available,
				'canBet' : canBet,
				'reason' : reason
			}
			logger.debug('group' + str(contexto['group']))
			logger.debug('available' + str(contexto['available']))
			logger.debug('canBet' + str(contexto['canBet']))
			logger.debug('reason' + str(contexto['reason']))
			return render(request, 'ubet/bet.html', contexto)
	elif request.method == 'POST':
		logger.debug('bet post')
		try:
			betpos = request.POST['bet_position']
			g = Group.objects.get(id=group_id)
			b = request.user.ubet_user.bet(g,betpos)
			if b[0]:
				return HttpResponseRedirect(reverse(group_info,args=[g.id]))
			contexto = {
				'toast' : b[1],
			}
			return render(request,'ubet/list_all_groups.html',contexto)


		except:
			raise
	return HttpResponse("welcome to limbo")