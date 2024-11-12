from django.db import models

class Discount(models.Model):
    
    id = models.AutoField(primary_key=True, db_column="id")    
    value = models.SmallIntegerField(unique = True, db_column="value")  

        
    def __str__(self):
        return f"Discount id: {self.id} \nValue: {self.value}%"
  