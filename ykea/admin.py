from django.contrib import admin
from .models import Item
from .models import ItemCnt
from .models import Shoppingcart
from .models import Client

admin.site.register(Item)
admin.site.register(Shoppingcart)
admin.site.register(ItemCnt)
admin.site.register(Client)
# Register your models here.
