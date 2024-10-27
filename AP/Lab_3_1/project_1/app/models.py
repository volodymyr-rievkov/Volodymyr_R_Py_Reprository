from django.db import models

class Delivery(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")  
    order = models.ForeignKey('Order', on_delete=models.CASCADE, unique=True, db_column="order_id")  
    country = models.CharField(max_length=50, db_column="country")  
    city = models.CharField(max_length=50, db_column="city")  
    street = models.CharField(max_length=50, db_column="street")  

    class Meta:
        managed = False
        db_table = 'delivery'
        
    def __str__(self):
        return f"Delivery id: {self.id} \nOrder: \n{self.order} \nCountry: {self.country} \nCity: {self.city} \nStreet: {self.street}"
    
class Discount(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")    
    value = models.SmallIntegerField(unique = True, db_column="value")  

    class Meta:
        managed = False
        db_table = 'discount'
        
    def __str__(self):
        return f"Discount id: {self.id} \nValue: {self.value}%"
    
class Order(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")  
    user = models.ForeignKey('User', on_delete=models.CASCADE, db_column="user_id") 
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_column="product_id")  
    amount = models.SmallIntegerField(db_column="product_amount") 
    comment = models.TextField(blank=True, null=True, db_column="comment") 
    date_time = models.DateTimeField(db_column="date_time")  
    total_price = models.DecimalField(max_digits=10, max_length=2, db_column="total_price")

    class Meta:
        managed = False
        db_table = 'order'
        
    def __str__(self):
        return f"Order id: {self.id} \nUser: {self.user.first_name} {self.user.last_name} \nProduct: {self.product.name} \nPrice: {self.product.price} \nAmount: {self.amount} \nDate/Time: {self.date_time} \nComment: {self.comment} \n-------------- \nTotal price: {self.total_price}"

class User(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")  
    first_name = models.CharField(max_length=50, db_column='first_name')
    last_name = models.CharField(max_length=50, db_column='last_name')
    phone_number = models.CharField(max_length=20, unique=True, db_column='phone_number')
    email = models.EmailField(max_length=50, unique=True, db_column='email')
    password = models.CharField(max_length=20, unique=True, db_column='password')

    class Meta:
        managed = False
        db_table = 'user'
        
    def __str__(self):
        return f"User id: {self.id} \nFirst Name: {self.first_name} \nLast name: {self.last_name} \nNumber: {self.phone_number} \nEmail: {self.email} \nPassword: {self.password}"

class Product(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")      
    name = models.CharField(max_length=50, unique=True, db_column="name")  
    info = models.TextField(blank=True, null=True, db_column="info")  
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column="price")  
    amount = models.IntegerField(db_column="amount")  
    discount = models.ForeignKey('Discount', blank=True, null=True, on_delete=models.SET_NULL, db_column="discount_id")  

    class Meta:
        managed = False
        db_table = 'product'

    def __get_discount_value(self):
        try:
            return self.discount.value if self.discount else 0.0
        except Discount.DoesNotExist:
            return 0.0
        
    def __str__(self):
        discount_value = self.__get_discount_value() 
        return f"Product id: {self.id} \nName: {self.name} \nPrice: {self.price} \nAmount: {self.amount} \nInfo: {self.info} \nDiscount: {discount_value}"
