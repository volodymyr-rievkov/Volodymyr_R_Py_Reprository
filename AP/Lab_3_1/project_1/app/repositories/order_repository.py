from app.models.order import Order
from app.models.user import User
from app.models.product import Product
from app.repositories.i_repository import IRepository
from django.utils import timezone

class OrderRepository(IRepository):
    def show_all(self):
        orders = Order.objects.all()
        for order in orders:
            print(order)
            print()
        print()
    
    def get_by_id(self, o_id):
        try:
            return Order.objects.get(id = o_id)
        except Order.DoesNotExist:
            print(f"Error: Order with id: {o_id} does not exist.")
            return None

    def __validate_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            print(f"Error: User with id: {user_id} does not exist.")
            return None

    def __validate_product(self, product_id, o_amount):
        try:
            product = Product.objects.get(id=product_id)
            if o_amount > product.amount:
                print(f"Error: Requested amount {o_amount} exceeds available amount {product.amount} for product id: {product_id}.")
                return None
            return product
        except Product.DoesNotExist:
            print(f"Error: Product with id: {product_id} does not exist.")
            return None

    def __validate_amount(self, amount, p_amount):
        if(amount <= 0):
            print("Error: Amount can not be negative.")
            return False
        elif(amount > p_amount):
            print(f"Error: Amount can not be more than '{p_amount}'.")
            return False   
        return True

    def create(self, user_id, product_id, o_amount, o_comment=None):
        user = self.__validate_user(user_id)
        if(not user):
            return None
        product = self.__validate_product(product_id, o_amount)
        if (not product):
            return None 
        if(not self.__validate_amount(o_amount, product.amount)):
            return None
        total = product.price * o_amount
        product.amount -= o_amount
        order = Order(
            user = user,
            product = product,
            amount = o_amount,
            date_time = timezone.now(),
            comment = o_comment,
            total_price = total
        )
        order.save()
        return order
    