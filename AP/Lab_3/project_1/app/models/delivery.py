from django.db import models

class Delivery(models.Model):
    
    id = models.AutoField(primary_key=True, db_column="id")  
    order = models.OneToOneField('Order', on_delete=models.CASCADE, unique=True, db_column="order_id")  
    country = models.CharField(max_length=50, db_column="country")  
    city = models.CharField(max_length=50, db_column="city")  
    street = models.CharField(max_length=50, db_column="street")  

    class Meta:
        managed = False
        db_table = 'delivery'
        
    def __str__(self):
        return f"Delivery id: {self.id} \nCountry: {self.country} \nCity: {self.city} \nStreet: {self.street} \nOrder: \n{self.order}"
   