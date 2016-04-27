from django.conf.urls import url

from . import views
urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login$', views.login, name='login'),
    url(r'^signup$',views.signup,name='signup'),
    url(r'^user_cp$',views.user_cp,name='user_cp'),
    url(r'^list_all_users$',views.list_all_users,name='list_all_users'),
    url(r'^logout$',views.logout,name='logout'),
    url(r'^list_all_groups$',views.list_all_groups,name='list_all_groups'),
    url(r'^new_group$',views.new_group,name='new_group'),
    url(r'^bet/(?P<group_id>[0-9]+)$', views.bet, name='bet'),
    url(r'^notification/(?P<group_id>[0-9]+)$', views.notification,name='notification'),
    url(r'^group_info/(?P<group_id>[0-9]+)$', views.group_info,name='group_info'),
    
    
]