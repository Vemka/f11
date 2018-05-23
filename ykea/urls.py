from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^items/$', views.items, name='items'),
    url(r'^items/(?P<category>.*)/$', views.items, name='items'),
    url(r'^item/(?P<item_number>.*)/$',views.item, name='item'),
    url(r'^shoppingcart/$', views.shoppingcart, name='shoppingcart'),
    url(r'^buy/$', views.buy, name='buy'),
    url(r'^delete/$', views.delete, name='delete'),
    url(r'^checkout/$', views.checkout, name='checkout'),
    url(r'^login/$',views.login_view,name='log'),
    url(r'^register/$', views.register, name='register')
]

 
