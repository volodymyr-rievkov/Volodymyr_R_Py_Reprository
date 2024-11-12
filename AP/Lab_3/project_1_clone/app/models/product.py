from django.db import models
from app.models.discount import Discount

class Product(models.Model):
    
    id = models.AutoField(primary_key=True, db_column="id")      
    name = models.CharField(max_length=50, unique=True, db_column="name")  
    info = models.TextField(blank=True, null=True, db_column="info")  
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column="price")  
    amount = models.IntegerField(db_column="amount")  
    discount = models.ForeignKey('Discount', blank=True, on_delete=models.SET_NULL, db_column="discount_id", null=True)  

    def __get_discount_value(self):
        try:
            return self.discount.value if self.discount else 0.0
        except Discount.DoesNotExist:
            return 0.0
        
    def __str__(self):
        discount_value = self.__get_discount_value() 
        return f"Product id: {self.id} \nName: {self.name} \nPrice: {self.price} \nAmount: {self.amount} \nInfo: {self.info} \nDiscount: {discount_value}"
