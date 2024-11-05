from django.db import models

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
