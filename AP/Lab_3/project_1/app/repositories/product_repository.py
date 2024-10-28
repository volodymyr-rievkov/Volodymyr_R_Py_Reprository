from app.models.product import Product
from app.models.discount import Discount
from app.repositories.i_repository import IRepository
from django.db import IntegrityError

class ProductRepository(IRepository):

    def get_all(self):
        return Product.objects.all()

    def show_all(self):
        products = Product.objects.all()
        for product in products:
            print(product)
            print()
        print()
    
    def get_by_id(self, p_id):
        try:
            return Product.objects.get(id = p_id)
        except Product.DoesNotExist:
            print(f"Error: Product with id: {p_id} does not exist.")
            return None

    def __validate_product_data(self, p_price, p_amount):
        if (p_price < 0):
            print("Error: Product price can not be negative.")
            return False
        if (p_amount < 0):
            print("Error: Product amount can not be negative.")
            return False
        return True

    def __get_discount(self, discount_id):
        if (discount_id):
            try:
                return Discount.objects.get(id=discount_id)
            except Discount.DoesNotExist:
                print(f"Error: Discount with id: {discount_id} does not exist.")
                return None

    def create(self, name, price, amount, info, discount_id=None):
        if (not self.__validate_product_data(price, amount)):
            return None
        discount = self.__get_discount(discount_id)
        product = Product(
            name = name,
            info = info,
            price = price - (price * (discount.value / 100)) if discount else price,
            amount = amount,
            discount = discount
        )
        try:
            product.save() 
            return product 
        except IntegrityError:
            print(f"Error: Product with name '{name}' already exists.")
            return None  

    def update(self, product, name=None, price=None, amount=None, discount_id=None):
        if (name is not None):
            product.name = name
        if (price is not None):
            product.price = price
        if (amount is not None):
            product.amount = amount
        if (discount_id is not None):
            product.discount_id = discount_id
        
        product.save()
        return product
