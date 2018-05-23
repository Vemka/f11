from django.contrib import admin
from .models import Item
from .models import ItemCnt
from .models import Shoppingcart

admin.site.register(Item)
admin.site.register(Shoppingcart)
admin.site.register(ItemCnt)
# Register your models here.
