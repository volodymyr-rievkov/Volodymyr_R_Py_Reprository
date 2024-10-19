from django.db import models

class Delivery(models.Model):
    delivery_id = models.AutoField(primary_key=True)  
    order = models.ForeignKey('Order', on_delete=models.CASCADE)  
    country = models.CharField(max_length=50)  
    city = models.CharField(max_length=50)  
    street = models.CharField(max_length=50)  

    def __str__(self):
        return f"Delivery id: {self.delivery_id} \nOrder id: {self.order.order_id} \nCountry: {self.country} \nCity: {self.city} \nStreet: {self.street}"
    
class Discount(models.Model):
    discount_id = models.AutoField(primary_key=True)  
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  
    discount_value = models.SmallIntegerField()  

    def __str__(self):
        return f"Discount id: {self.discount_id} \nProduct id: {self.product.product_id} \nValue: {self.discount_value}%"
    
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)  
    user = models.ForeignKey('User', on_delete=models.CASCADE) 
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  
    product_amount = models.SmallIntegerField()  
    order_comment = models.TextField(blank=True, null=True)  

    def __str__(self):
        return f"Order id: {self.order_id} \nUser id: {self.user.user_id} \nProduct id: {self.product.product_id} \nAmount: {self.product_amount} \nComment: {self.order_comment}"

class OrderHistory(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)  
    order_date_time = models.DateTimeField()

    def __str__(self):
        return f"Order id: {self.order.order_id} \nDate/Time: {self.order_date_time}"

class User(models.Model):
    user_id = models.AutoField(primary_key=True)  
    user_first_name = models.CharField(max_length=50)  
    user_last_name = models.CharField(max_length=50)  
    user_phone_number = models.CharField(max_length=20)  
    user_email = models.EmailField(max_length=50, unique=True)  
    user_password = models.CharField(max_length=20)  

    def __str__(self):
        return f"User id: {self.user_id} \nFirst Name: {self.user_first_name} \nLast name: {self.user_last_name} \nNumber: {self.user_phone_number} \nEmail: {self.user_email} \nPassword: {self.user_password}"

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)      
    product_name = models.CharField(max_length=50)  
    product_info = models.TextField(blank=True, null=True)  
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  
    product_amount = models.IntegerField()  
    discount = models.ForeignKey('Discount', blank=True, null=True, on_delete=models.SET_NULL)  

    def __str__(self):
        return f"Product id: {self.product_id} \nName: {self.product_name} \nPrice: {self.product_price} \nAmount: {self.product_amount} \nInfo: {self.product_info} \nDiscount id: {self.discount.discount_id if self.discount else 'None'}"
        