# coding: utf-8


from django.shortcuts import render
from ubet.forms import UserSignupForm, UserAuthenticationForm

# Create your views here.

def login(request):
	form = UserAuthenticationForm()
	logger.debug('login')

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		

		user = authenticate(username=username, password=password)

		if user is not None:
			if user.is_active:
				auth_login(request, user)
				return HttpResponseRedirect('ubet/user_cp.html')

				login(request, user)
				return HttpResponseRedirect('ubet/user_cp.html')
			else:
				return render(request, 'ubet/login.html', { 'login_msg': 'Conta desativada.', 'form': form })
		else:
			return render(request, 'ubet/login.html', { 'login_msg': 'Combinação de usuário e senha incorreta.', 'form': form })
	else:
		return render(request, 'ubet/login.html', { 'form': form })


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
	logger.debug('user_cp')
	if request.user.is_authenticated():
		return render(request, 'ubet/user_cp.html')
	else:
		form = UserAuthenticationForm()
		return render(request, 'ubet/login.html', { 'login_msg': 'Você precisa estar logado para acessar essa página.', 
												 'form': form })

