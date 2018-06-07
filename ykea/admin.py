from django.contrib import admin
from .models import Item
from .models import ItemCnt
from .models import Shoppingcart
from .models import Client
from .models import ItemHist
from .models import Bill

admin.site.register(Item)
admin.site.register(Shoppingcart)
admin.site.register(ItemCnt)
admin.site.register(Client)
admin.site.register(ItemHist)
admin.site.register(Bill)
# Register your models here.
