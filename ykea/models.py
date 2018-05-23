from django.db import models

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
    featured_photo = models.ImageField()
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
    count=models.IntegerField(default=1)
    def create(cls, sCartId, itemId):

        itemCnt = cls(Shoppingcart_id=sCartId, Item_id=itemId)
        itemCnt.count = 1
        # do something with the book
        return itemCnt  #sCart
 #   count = models.DecimalField(max_digits=8, decimal_places=2)
