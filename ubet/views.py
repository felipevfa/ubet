
# coding: utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from ubet.forms import UserSignupForm, UserAuthenticationForm,new_group_Form
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ubet.models import Ubet_user,User,Group,Notification
import urllib2
import requests
from django.contrib import messages
from django.template import RequestContext
import datetime,logging
from django.utils import timezone
# Create your views here.
from django.utils.translation import ugettext_lazy as _
logger = logging.getLogger(__name__)

from ipware.ip import get_ip



@login_required()
def list_waiting(request):
	"""mostra ao usuario os grupos ativos em que ele ainda nao apostou"""
	logger.debug('list_waiting')
	groups = Group.active_groups(request.user);
	return render(request,'ubet/list_all_groups.html', {'grupos': groups, 'waiting': True, 'waiting_active': 'active' })

@login_required()
def list_my_active_bets(request):
	"""mostra ao usuario os grupos ativos em que ele ja apostou"""
	logger.debug('list_all_groups')
	groups = Group.active_groups(request.user,waiting=True);
	return render(request,'ubet/list_all_groups.html', {'grupos': groups, 'my_bets': True, 'bets_active': 'active' })

@login_required()
def new_group(request):
	
	logger.debug('new_group')
	if request.method == 'POST':
		logger.debug('new_group post')
		form = new_group_Form(request.POST)
		if form.is_valid():
			gl = Group.objects.filter(status='WAITING',creator=request.user,bet_value=form.cleaned_data['bet_value'])
			if (len(gl) > 0):
				toast = _('You cannot own two active groups with equal bet values.')
				return render(request,'ubet/new_group.html',{'form':form,'toast':toast})
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
	"""gerencia o formulario para um novo usuario.
	Aqui se encontra o recaptcha do google. Recomenda-se alterar sua propriedades para uma conta
	do administrador do site. (O recaptcha e gratuito)
	Esta view e o login sao as unicas views que nao exigem login."""
	logger.debug('signup')
	error_msg = ''

	if request.method == 'POST':
		logger.debug('signup post')
		data = {
			'secret' : '6Ld3zx4TAAAAAFqv0XY3skJWCVO4_DTSRLBU3IOZ',
			# para testes, apague essa linha (1/2)
			'response' : request.POST['g-recaptcha-response'],
			'remoteip' : get_ip(request),
		}
		s = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)

		form = UserSignupForm(request.POST)
		logger.debug(form)

		### para testes, apague essas linhas (2/2)
		if not s.json()['success']:
			return render(request,'ubet/signup.html',{'form':form,'toast':_("Check the reCaptcha, please")})


		if form.is_valid():
			logger.debug('signup e valido')
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
	if request.method == 'POST':		
		username = request.POST['username']
		password = request.POST['password']
		logger.debug(username + 'logandoo')
		user = authenticate(username=username, password=password)

		if user is not None:
			if user.is_active:
				auth_login(request, user)
				return redirect(reverse('list_waiting'))
			else:
				return render(request, 'ubet/login.html', { 'toast': _('Account disabled'), 'form': form })
		else:
			return render(request, 'ubet/login.html', { 'toast': _('Username and password do not match'), 'form': form })
	else:
		if request.user.is_active:
			return HttpResponseRedirect(reverse('list_waiting'))
		msg = _("Welcome")
		return render(request, 'ubet/login.html', { 'form': form ,'toast':msg})

@login_required()
def logout(request):
	logger.debug('logout')
	auth_logout(request)
	return HttpResponseRedirect(reverse('login'))


@login_required()
def user_cp(request):
	"""user command panel: painel de controle
	nessa pagina o usuario pode ver suas informacoes, as ultimas notificacoes 
	e ter acesso a seu historico"""
	logger.debug('user_cp')
	user_groups = Group.groups_by_user(request.user)
			
	notificacoes =  Notification.objects.filter(user=request.user)
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

@login_required()
def notification(request,group_id):
	""" esta view existe para redirecionar do user_cp para o grupo adequado, 
	quando o usuario clica em uma notificacao. Sua existencia se faz necessaria
	para apagar a notificacao do banco."""
	logger.debug('notification')
	n = Notification.objects.get(id=group_id)
	g = n.group.id
	logger.debug(n)
	logger.debug(g)
	n.delete()
	return HttpResponseRedirect(reverse(group_info,args=[g]))

@login_required()	
def group_info(request,group_id):
	"""exibe informacoes acerca do grupo
	casos a se tratar: 
	- o group_id e invalido.
	- o usuario nao pode apostar no grupo que esta observando, tornando indisponivel o botao de aposta"""
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
	toast = ""
	remaining = ''
	if g.status == 'WAITING':
		remaining =  g.time_left()
		if request.user in user_list:
			toast = _("You are in this group")
		else:
			toast = _("You are not in this group")
	elif g.status == "FINISHED":
		u = request.user
		if request.user in user_list:
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
		'groupname': g.name, 
		'canBet': canBet, 
	 	'warning': warning ,
	 	'toast' : toast,
	 	'remaining' : remaining,
	 	'sim_list' : sl,
	 	'reward' : g.get_prize(),
	}
	logger.debug('users ' + unicode(contexto['users']))
	logger.debug('group ' + unicode(contexto['group']))
	logger.debug('groupname ' + unicode(((contexto['groupname']))))
	logger.debug('canBet ' + unicode(contexto['canBet']))
	logger.debug('warning ' + unicode(contexto['warning']))
	logger.debug('toast ' + unicode(contexto['toast']))
	logger.debug('remaining ' + unicode(contexto['remaining']))
	logger.debug('sim_list ' + unicode(contexto['sim_list']))
	logger.debug('reward ' + unicode(contexto['reward']))
	return render(request, 'ubet/group_info.html',contexto )


@login_required()
def bet(request,group_id):
	"""pagina com posicoes dos participantes em um grupo, dando ao usuario a possibilidade de apostar.
	A diferenca basica entre a view group_info, alem da possibilidade de apostar, e que essa pagina
	nao e focada em mostrar informacoes do grupo. Ela se torna irrelevante qunando o grupo esta finalizado.
	Casos a tratar:
	- o group_id nao pertence a nenhum grupo
	- o usuario nao pode apostar nesse grupo
	- a aposta deixa de ser possivel no intervalo entre o get e o post
	"""
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
			# Verifica se o usuário tem mesmo créditos para apostar
			available = group.sim_list()
			x = group.possible_bet(request.user)
			canBet = x[0]
			reason = x[1]
			abouttoend = False
			if group.cur_size() == group.max_size-1:
				abouttoend = True
			contexto = {
				'abouttoend' : abouttoend,
				'group' : group,
				'available' : available,
				'canBet' : canBet,
				'reason' : reason
			}
			logger.debug('group' + str(contexto['group']))
			logger.debug('available' + str(contexto['available']))
			logger.debug('canBet' + str(contexto['canBet']))
			logger.debug(('reason' + unicode(contexto['reason'])))	
			return render(request, 'ubet/bet.html', contexto)
		else:
			return render(request,'ubet/bet.html',{'toast':_('Sorry, this group does not exist.')})
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
			return render(request,'ubet/list_waiting.html',contexto)


		except:
			raise
	return HttpResponse("welcome to limbo")

@login_required()
def group_log(request):
	"""gera a pagina com historico completo de grupos do usuario"""
	logger.debug('group history')
	
	groups = Group.groups_by_user(request.user)
	paginator = Paginator(groups, 15)
	page = request.GET.get('page')


	try:
		group_list = paginator.page(page)
	except PageNotAnInteger:
		group_list = paginator.page(1)
	except EmptyPage:
		group_list = paginator.page(paginator.num_pages);

	contexto = {
		'page': group_list,
		'paginator': paginator
	}

	return render(request, 'ubet/group_log.html', contexto)
