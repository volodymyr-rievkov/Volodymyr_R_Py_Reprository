from django.db import models

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
