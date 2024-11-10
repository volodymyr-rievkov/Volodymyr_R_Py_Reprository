from app.models.discount import Discount
from app.repositories.i_repository import IRepository

from django.db import IntegrityError

class DiscountRepository(IRepository):

    def get_all(self):
        return Discount.objects.all()

    def show_all(self):
        discounts = Discount.objects.all()
        for discount in discounts:
            print(discount)
            print()
        print()
    
    def get_by_id(self, d_id):
        try:
            return Discount.objects.get(id = d_id)
        except Discount.DoesNotExist:
            print(f"Error: Discount with id: {d_id} does not exist.")
            return None
        
    def __validate_discount_value(self, d_value):
        if (0 >= d_value or d_value >= 100):
            print("Error: Discount value is not valid.")
            return False
        return True

    def create(self, value):
        if (not self.__validate_discount_value(value)):
            return None
        discount = Discount(
            value = value
        )
        try:
            discount.save()
            return discount
        except IntegrityError:
            print(f"Error: A discount with value {value}% already exists.")
            return None

    def update(self, discount, value=None):
        if (value is not None):
            discount.value = value
        
        discount.save()
        return discount
