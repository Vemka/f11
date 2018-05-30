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

from random import randint

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from ykea.permissions import IsCommercialOrReadOnly
from rest_framework import permissions

def index(request):
    context = {
        'categories': Item.CATEGORIES,
    }
    if(request.user.is_authenticated()):
        context['current_user'] = request.user

    return render(request, 'ykea/index.html', context)


def items(request,category=""):
    items_by_category = Item.objects.filter(category=category)
    context = {
        'items': items_by_category,
        'category': category,
    }
    if (request.user.is_authenticated()):
        context['current_user'] = request.user

    return render(request, 'ykea/items.html', context)
	
	
def item(request,item_number=""):

    try:
        item = Item.objects.get(item_number=item_number)
        context = {
            'item': item,
        }
    except Item.DoesNotExist:
        context = {}
    if (request.user.is_authenticated()):
        context['current_user'] = request.user

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
@login_required
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
    finalPrice = 0
    itemTuples=[]
    for it in itemCountsList:
        finalPrice += it.itemId.price * it.count
        itemTuples.append((it.itemId.item_number,it.itemId.name,it.count,it.itemId.price,it.count *  it.itemId.price))

    context = {
        'Cart': sc,
        'items': itemTuples,
        'balance': request.user.client.money - finalPrice,
        'price': finalPrice
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
    request.user.client.money-=finalPrice
    request.user.client.save()
    return render(request, 'ykea/checkout.html', context)

def login_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None:# and user.is_active:
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
    return HttpResponseRedirect("/ykea/")


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            auth.login(request, new_user)
            return HttpResponseRedirect(reverse("index"))
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })

class ItemViewSet(viewsets.ModelViewSet):
    """api endpoint"""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsCommercialOrReadOnly,)
    queryset=Item.objects.all().order_by('item_number')
    serializer_class = ItemSerializer


    def get_queryset(self):
        """
        Optionally restricts the returned items to a given category, max price and if items are new,
        by filtering against a `corresponding parameters in the URL.
        """
        queryset = Item.objects.all()
        cat = self.request.query_params.get('category', None)
        isNew = self.request.query_params.get('new', None)
        priceMax = self.request.query_params.get('price', None)

        if cat is not None:
            queryset = queryset.filter(category=cat)

        if isNew is not None:
            if isNew == 'yes':
                queryset = queryset.filter(is_new=True)
            elif isNew == 'no':
                queryset = queryset.filter(is_new=False)

        if priceMax is not None:
            queryset = queryset.filter(price__lte = priceMax)


        return queryset


@login_required
def printmoney(request):
    a= randint(0,10)
    context = {}
    if a<5:
        request.user.client.money=0
        request.user.client.save()
    else:
        request.user.client.money += a*1337
        request.user.client.save()
        context = {
            'sum': a,
            }
    return render(request, "ykea/money.html", context)