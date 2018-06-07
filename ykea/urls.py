from django.conf.urls import url


from . import views

listOfAddresses = ["161.116.56.65","161.116.56.165","127.0.0.1:8000"]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^items/$', views.items, name='items'),
    url(r'^items/(?P<category>.*)/$', views.items, name='items'),
    url(r'^item/(?P<item_number>.*)/$',views.item, name='item'),
    url(r'^shoppingcart/$', views.shoppingcart, name='shoppingcart'),
    url(r'^buy/$', views.buy, name='buy'),
    url(r'^delete/$', views.delete, name='delete'),
    url(r'^checkout/$', views.checkout, name='checkout'),
    url(r'^login/$',views.login_view,name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^print/$', views.printmoney, name='print'),
    url(r'^comparator$', views.comparator, {'ips': listOfAddresses},name='comparator'),
]

 
