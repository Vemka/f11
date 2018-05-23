from django.shortcuts import render

from django.http import HttpResponse,HttpResponseRedirect
from .models import Item
from .models import Shoppingcart
from .models import ItemCnt
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import ItemSerializer
from django.contrib.auth.decorators import login_required

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render

def index(request):
    context = {
        'categories': Item.CATEGORIES,
    }
    return render(request, 'ykea/index.html', context)
	#return HttpResponse("Hello, world. You're at the ykea home.")


def items(request,category=""):
    items_by_category = Item.objects.filter(category=category)
    context = {
        'items': items_by_category,
        'category': category,
    }
    return render(request, 'ykea/items.html', context)
	
	
def item(request,item_number=""):
    item= Item.objects.filter(item_number=item_number)
    context = {
        'item': item,
    }
    return render(request, 'ykea/item.html', context)

def shoppingcart(request):
    #if "selectedItem" in request.session:
    #	  selectedItems = request.session["selectedItem"]
    #else:
    selectedItems = []
    for key in request.POST:
        if key.startswith("checkbox"):
            selectedItems.append(request.POST[key])
    request.session["selectedItem"] = selectedItems
    return HttpResponseRedirect(reverse('buy'))

def buy(request):
    if "shoppingcartID" in request.session:
        sCartId = request.session["shoppingcartID"]
    else:
        #print ("entramos en segundo if")
        sCart = Shoppingcart.objects.create()
        request.session["shoppingcartID"] = sCart.id
        sCartId = sCart.id
    try:
        sc = Shoppingcart.objects.get(id=sCartId)
    except Shoppingcart.DoesNotExist:
        sc = Shoppingcart.objects.create()
        request.session["shoppingcartID"] = sc.id
        sCartId = sc.id
    for itemId in request.session["selectedItem"]:
        item = Item.objects.get(item_number=itemId)
        try:
            itemCnt=ItemCnt.objects.get(sCartId=sc, itemId=item)
            itemCnt.count = itemCnt.count + 1
            itemCnt.save()
            #break
        except ItemCnt.DoesNotExist:
            itemCnt = ItemCnt.objects.create(sCartId=sc, itemId=item)

    itemCountsList = ItemCnt.objects.filter(sCartId=sCartId)
    itemTuples=[]
    for it in itemCountsList:

        itemTuples.append((it.itemId.item_number,it.itemId.name,it.count,it.itemId.price,it.count *  it.itemId.price))
    context = {
        'Cart': sc,
        'items': itemTuples
    }
    request.session["selectedItem"] = []
    return render(request, 'ykea/shoppingcart.html', context)

def delete(request):
    selectedItems = []
    for key in request.POST:
        if key.startswith("checkbox"):
            selectedItems.append(request.POST[key])


    if "shoppingcartID" in request.session:
        sCartId = request.session["shoppingcartID"]
    else:
        #print ("entramos en segundo if")
        sCart = Shoppingcart.objects.create()
        request.session["shoppingcartID"] = sCart.id
        sCartId = sCart.id
    sc = Shoppingcart.objects.get(id=sCartId)
    for itemId in selectedItems:
        item = Item.objects.get(item_number=itemId)
        try:
            itemCnt=ItemCnt.objects.get(sCartId=sc, itemId=item).delete()
            #break
        except ItemCnt.DoesNotExist:
            print("WARNING deleting non existent item in a cart")
            #itemCnt = ItemCnt.objects.create(sCartId=sc, itemId=item)
    request.session["selectedItem"] = []
    return HttpResponseRedirect(reverse('buy'))


@login_required
def checkout(request):
    if "shoppingcartID" in request.session:
        sCartId = request.session["shoppingcartID"]
    else:
        sCart = Shoppingcart.objects.create()
        request.session["shoppingcartID"] = sCart.id
        sCartId = sCart.id
    sc = Shoppingcart.objects.get(id=sCartId)
    finalItems=ItemCnt.objects.filter(sCartId=sc)
    result=[]
    finalPrice=0
    for it in finalItems:
        result.append(
            (it.itemId.item_number, it.itemId.name, it.count, it.itemId.price, it.count * it.itemId.price))
        finalPrice+=it.count * it.itemId.price
        context = {
            'items': result,
            'price': finalPrice
        }
    ItemCnt.objects.filter(sCartId=sc).delete()
    if len(result)!=0:
        sc.delete()
    del request.session["shoppingcartID"]
    return render(request, 'ykea/checkout.html', context)

def login_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
        auth.login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect("index")
    else:
        # Show an error page
        return HttpResponseRedirect("/account/invalid/")

def logout_view(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/account/loggedout/")


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })

class ItemViewSet(viewsets.ModelViewSet):
    """api endpoint"""
    queryset=Item.objects.all().order_by('item_number')
    serializer_class = ItemSerializer
