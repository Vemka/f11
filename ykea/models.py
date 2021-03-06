from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save



# Create your models here.
class Item(models.Model):
    CATEGORIES = (
        ("beds", "Beds & mattressess"),
        ("furn", "Furniture, wardrobes & shelves"),
        ("sofa", "Sofas & armchairs"),
        ("table", "Tables & chairs"),
        ("texti","Textiles"),
        ("deco","Decoration & mirrors"),
        ("light","Lighting"),
        ("cook","Cookware"),
        ("tablw","Tableware"),
        ("taps","Taps & sinks"),
        ("org", "Organisers & storage accesories"),
        ("toys","Toys"),
        ("leis","Leisure"),
        ("safe","safety"),
        ("diy", "Do-it-yourself"),
        ("floor","Flooring"),
        ("plant","Plants & gardering"),
        ("food","Food & beverages")
    )
    item_number = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_new = models.BooleanField()
    size = models.CharField(max_length=40)
    instructions = models.TextField()
    featured_photo = models.ImageField(upload_to="staticfiles")
    category = models.CharField(max_length=5, choices=CATEGORIES)
    def __str__(self):
        return  ('[**NEW**]' if self.is_new else '') + "[" + self.category + "] [" + self.item_number + "] " + self.name + " - " + self.description + " (" + self.size + ") : " + str(self.price) + " €"

class Shoppingcart(models.Model):
    id=models.AutoField(primary_key=True)

    items=models.ManyToManyField(
        Item,
        through='ItemCnt',
        #through_fields=('sCartId', 'itemId'),
        #ItemCnt;
        #through='ItemCnt'
    )
    def create(cls):
        sCart = cls()
        # do something with the book
        return sCart
    #def create_itemCnt(self):


    
class ItemCnt(models.Model):
    sCartId = models.ForeignKey("Shoppingcart")
    itemId = models.ForeignKey("Item")
    count = models.IntegerField(default=1)
    def create(cls, sCartId, itemId):

        itemCnt = cls(Shoppingcart_id=sCartId, Item_id=itemId)
        itemCnt.count = 1
        # do something with the book
        return itemCnt  #sCart

class ItemHist(models.Model):
    billId = models.ForeignKey("Bill")
    itemId = models.ForeignKey("Item")
    count = models.IntegerField(default=1)
    def create(cls, billId, itemId):

        itemH = cls(billId=billId, Item_id=itemId)
        itemH.count = 1
        return itemH

class Bill(models.Model):
    id=models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items=models.ManyToManyField(
        Item,
        through='ItemHist',
    )
    def create(cls,userId):

        bill = cls(user=userId)
        return bill





class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name ='client',unique=True)
    money = models.IntegerField(default=10000)


def save_client(sender, instance=False,**kwargs):
    try:
        Client.objects.get(user=instance)
    except Client.DoesNotExist:
        client=Client.objects.create(user=instance)
        client.save()

post_save.connect(save_client, sender=User)