from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^signup$',views.signup,name='signup'),
    url(r'^user_cp$',views.user_cp,name='user_cp'),
]