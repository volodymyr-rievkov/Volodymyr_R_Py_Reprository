from app.models.delivery import Delivery
from app.models.order import Order
from app.repositories.i_repository import IRepository
from django.db import IntegrityError

class DeliveryRepository(IRepository):

    def get_all(self):
        return Delivery.objects.all()

    def show_all(self):
        deliveries = Delivery.objects.all()
        for delivery in deliveries:
            print(delivery)
            print()
        print()

    def get_by_id(self, d_id):
        try:
            return Delivery.objects.get(id = d_id)
        except Delivery.DoesNotExist:
            print(f"Error: Delivery with id: {d_id} does not exist.")
            return None
        
    def __validate_order_exists(self, order_id):
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            print(f"Error: Order with id: {order_id} does not exist.")
            return None  

    def create(self, order_id, country, city, street):
        order = self.__validate_order_exists(order_id)
        if (not order):
            return None
        delivery = Delivery(
            order = order,
            country = country,
            city = city,
            street = street
        )
        try:
            delivery.save()  
            return delivery
        except IntegrityError:
            print(f"Error: Delivery for order {order_id} already exists.")
            return None  
    
    def update(self, delivery, order_id=None, country=None, city=None, street=None):
        if (order_id is not None):
            delivery.order_id = order_id
        if (country is not None):
            delivery.country = country
        if (city is not None):
            delivery.city = city
        if (street is not None):
            delivery.street = street
        
        delivery.save()
        return delivery
