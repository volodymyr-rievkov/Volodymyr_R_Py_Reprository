from django.db import models

class Delivery(models.Model):
    id = models.AutoField(primary_key=True)  
    order = models.ForeignKey('Order', on_delete=models.CASCADE)  
    country = models.CharField(max_length=50)  
    city = models.CharField(max_length=50)  
    street = models.CharField(max_length=50)  

    class Meta:
        managed = False
        db_table = 'delivery'
        
    def __str__(self):
        return f"Delivery id: {self.id} \nOrder: \n{self.order} \nCountry: {self.country} \nCity: {self.city} \nStreet: {self.street}"
    
class Discount(models.Model):
    id = models.AutoField(primary_key=True)  
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='discounts')  
    value = models.SmallIntegerField()  

    class Meta:
        managed = False
        db_table = 'discount'
        
    def __str__(self):
        return f"Discount id: {self.id} \nProduct: \n{self.product} \nValue: {self.value}%"
    
class Order(models.Model):
    id = models.AutoField(primary_key=True)  
    user = models.ForeignKey('User', on_delete=models.CASCADE) 
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  
    amount = models.SmallIntegerField()  
    comment = models.TextField(blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'оrder'
        
    def __str__(self):
        return f"Order id: {self.id} \nUser: \n{self.user} \nProduct: \n{self.product} \nAmount: {self.amount} \nComment: {self.comment}"

class OrderHistory(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)  
    order_date_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'order_history'
        
    def __str__(self):
        return f"Order: \n{self.order} \nDate/Time: {self.order_date_time}"

class User(models.Model):
    id = models.AutoField(primary_key=True)  
    first_name = models.CharField(max_length=50)  
    last_name = models.CharField(max_length=50)  
    phone_number = models.CharField(max_length=20)  
    email = models.EmailField(max_length=50, unique=True)  
    password = models.CharField(max_length=20)  

    class Meta:
        managed = False
        db_table = 'user'
        
    def __str__(self):
        return f"User id: {self.id} \nFirst Name: {self.first_name} \nLast name: {self.last_name} \nNumber: {self.phone_number} \nEmail: {self.email} \nPassword: {self.password}"

class Product(models.Model):
    id = models.AutoField(primary_key=True)      
    name = models.CharField(max_length=50)  
    info = models.TextField(blank=True, null=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    amount = models.IntegerField()  
    discount = models.ForeignKey('Discount', blank=True, null=True, on_delete=models.SET_NULL, related_name='products')  

    class Meta:
        managed = False
        db_table = 'product'

    def __str__(self):
        return f"Product id: {self.id} \nName: {self.name} \nPrice: {self.price} \nAmount: {self.amount} \nInfo: {self.info} \nDiscount: {self.discount.discount_value if self.discount else '0.0'}%"
