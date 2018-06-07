from django.shortcuts import render

from django.http import HttpResponse,HttpResponseRedirect
from .models import Item
from .models import Shoppingcart
from .models import ItemCnt
from .models import ItemHist
from .models import Bill
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
    if(category==""):
        items_by_category=Item.objects.all
    else:
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
            val=request.POST["textbox"+str(request.POST[key])]
            try:
                valInt = int(val)
            except ValueError:
                valInt = 1
            valInt=abs(valInt)
            if valInt != 0:
                selectedItems.append((request.POST[key],valInt))
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
    context={}
    if "selectedItem" in request.session.keys():
        for itemId in request.session["selectedItem"]:
            item = Item.objects.get(item_number=itemId[0])
            try:
                itemCnt=ItemCnt.objects.get(sCartId=sc, itemId=item)
                itemCnt.count = itemCnt.count + itemId[1]
                itemCnt.save()
                #break
            except ItemCnt.DoesNotExist:
                itemCnt = ItemCnt.objects.create(sCartId=sc, itemId=item)
                itemCnt.count = itemId[1]
                itemCnt.save()

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
    finalItems = ItemCnt.objects.filter(sCartId=sc)
    histBills = Bill.objects.filter(user=request.user)
    resultHist=[]
    histPrice = 0
    #saving previous purchases as tuples for html template
    for bill in histBills:
        billH=[]
        histItems = ItemHist.objects.filter(billId=bill)
        for itemH2 in histItems:
            billH.append(
                (itemH2.itemId.item_number, itemH2.itemId.name, itemH2.count, itemH2.itemId.price,
                 itemH2.count * itemH2.itemId.price))
            histPrice += itemH2.count * itemH2.itemId.price
        resultHist.append(billH)

    #saving current purchased items in bill history
    if len(finalItems)!=0:

        bill=Bill.objects.create(user=request.user)

    for itemCn in finalItems:
        itemH = ItemHist.objects.create(billId=bill, itemId=itemCn.itemId)
        itemH.count=itemCn.count
        itemH.save()





    result=[]
    finalPrice=0
    for it in finalItems:
        result.append(
            (it.itemId.item_number, it.itemId.name, it.count, it.itemId.price, it.count * it.itemId.price))
        finalPrice+=it.count * it.itemId.price
        context = {
            'items': result,
            'price': finalPrice,
            'billsH': resultHist,
            'priceH': histPrice
        }
    if len(finalItems) == 0:
        context = {
            'billsH': resultHist,
            'priceH': histPrice
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

def comparator(request,**kwargs):
    #print(kwargs)

    context = {
        'ips': kwargs['ips'],
    }

    return render(request, "ykea/comparator.html", context)