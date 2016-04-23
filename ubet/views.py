
# coding: utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ubet.forms import UserSignupForm, UserAuthenticationForm,new_group_Form
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from ubet.models import Ubet_user,User,Group,Notification
from rayquasa.settings import TIME_TO_EXPIRE,GROUP_MAX_CAPATICY as expire,gmaxcap
from django.contrib import messages
from django.template import RequestContext
import datetime,logging
from django.utils import timezone
# Create your views here.
from django.utils.translation import ugettext as _
logger = logging.getLogger(__name__)
@login_required()
def list_all_groups(request):
	if request.user.is_authenticated():
		groups = Group.active_groups();

		users_by_group = {}

		for g in groups:
			g.user_list = list(Group.users_by_group(g))

		return render(request,'ubet/list_all_groups.html', {'grupos': groups })

	form = UserAuthenticationForm()
	return render(request, 'ubet/login.html', { 'form': form, 'toast': _('You need to be logged in to access this page.')})

@login_required()
def new_group(request):
	error_msg = { 'size_error': "",
				  'bet_error': ""
				}
	if request.method == 'POST':
		form = new_group_Form(request.POST, request.FILES)
		has_db_errors = False

		if form.is_valid():
			errors = form.check_values()

		#	if errors['position_error']:
		#		error_msg = error_msg + 'Posicao invalida.<br>'
		#		has_db_errors = True

			if errors['max_size_error']:
				error_msg['size_error'] = _('A group must have two members at least, and at most '+ str(gmaxcap))
				has_db_errors = True

			if errors['bet_value_error']:
				error_msg['bet_error'] = _('The bet must has a positive value.')
				has_db_errors = True


			if has_db_errors:
				return render(request, 'ubet/new_group.html', { 'form': form, 'new_groups_msg': error_msg })
			else:
				group = form.save(request.user)
				return HttpResponseRedirect(reverse(bet,args=[group.id]))
				# group.update()
				available = [None]*group.max_size 
				# return HttpResponseRedirect(reverse(group_info,args=[group.id]))
				if request.user.ubet_user.creditos < group.bet_value:
					canBet = False
					toast = _('Not enough credits')
				else:
					toast = ""
					canBet = True
				return render(request, 'ubet/bet.html', {'group': group, 'available': available, 'new': True ,'canBet': canBet,'toast':toast})
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
				error_msg = error_msg + _('Username taken') + '.<br>'
				has_db_errors = True

			if errors['email_error']:
				error_msg = error_msg + _('E-mail taken') + '.<br>'
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
	logger.debug('login')
	logger.error('login')

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		logger.debug(username + 'logandoo')
		user = authenticate(username=username, password=password)

		if user is not None:
			if user.is_active:
				auth_login(request, user)
				msg = "Olá, {}".format(user.username)
				return render(request,'ubet/list_all_groups.html',{'toast':msg})
			else:
				return render(request, 'ubet/login.html', { 'toast': _('Account disabled'), 'form': form })
		else:
			return render(request, 'ubet/login.html', { 'toast': _('Username and assword do not match'), 'form': form })
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
	user_groups = Group.groups_by_user(request.user)
			
	notificacoes =  Notification.objects.filter(user=request.user)
	if request.user.is_authenticated():
		contexto = {
			'user': request.user, 
			'user_groups': user_groups,
			'notification' : notificacoes,
		}
		return render(request, 'ubet/user_cp.html', contexto)
	else:
		form = UserAuthenticationForm()
		return render(request, 'ubet/login.html', { 'login_msg': _('Only logged users can access this page'),
												 'form': form })

@login_required()
def notification(request,group_id):
	n = Notification.objects.get(id=group_id)
	g = n.group.id
	n.delete()

	return HttpResponseRedirect(reverse(group_info,args=[g]))
	
@login_required()	
def group_info(request,group_id):
	try:
		g = Group.objects.get(id=group_id)
		g.update()
	except ObjectDoesNotExist:
		return render(request, 'ubet/group_info.html', { 'error_msg': _('Sorry, this grops does not exist.'), 'p_title': 'Erro' })			

	u = g.users_by_group()
	user_list = u[0]
	position_list = u[1]
	canBet = False
	warning = ""
	toast = "masqbelo toast"
	if g.status == 'WAITING':
		remaining =  expire - (timezone.now() - g.date_of_birth).seconds / 60
		strinfo = _("Active group. Time remaining for conclusion: ") + str(remaining )+ "m."
		if request.user in user_list:
			toast = _("You are in this group")
		else:
			toast = _("You are not in this group")
	elif g.status == "FINISHED":
		strinfo = _("Group finished. The winner is: ")+ str(g.winner.first_name)
		u = request.user
		if request.user in g.users_by_group()[0]:
			strinfo += '\n'
			if request.user != g.winner:
				strinfo +=  _("Voce perdeu: ")  + str(g.bet_value)
				toast = "Voce perdeu essa aposta"
			else:
				strinfo += _("Voce ganhou: ") +str(g.bet_value*g.max_size)
				toast = _("Voce ganhou essa aposta")
	elif g.status == "CANCELED":
		strinfo = _("Grupo cancelado. Apostas extornadas.")
		toast = _("Grupo cancelado")

	if request.user in user_list:
		warning = _('Você já apostou nesse grupo.')
	else:
		if request.user.ubet_user.creditos < g.bet_value:
			warning = 'Você não tem créditos suficientes para apostar.'
		else:
			canBet = True

	if g.status == "CANCELED":
		canBet = False
	contexto = {'group': g, 
		'users': zip(user_list, position_list), 
		'p_title': g.name, 
		'canBet': canBet, 
	 	'warning': warning ,
	 	'strinfo' : strinfo,
	 	'toast' : toast,
	 }
	return render(request, 'ubet/group_info.html',contexto )


	#else:
	#	form = UserAuthenticationForm()
	#	return render(request, reverse('login'), { 'login_msg': 'Você precisa conectar-se para ver os grupos.',
	#												'form': form })

@login_required()
def bet(request,group_id):
	# Se há um novo grupo sendo criado, recupera ele através de Sessions.
	if request.method == 'GET':
		try:
			group = Group.objects.get(id=group_id)
		except ObjectDoesNotExist:
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
			return render(request, 'ubet/bet.html', contexto)
	elif request.method == 'POST':
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