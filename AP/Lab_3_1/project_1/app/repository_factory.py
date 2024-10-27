from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.discount_repository import DiscountRepository
from app.repositories.delivery_repository import DeliveryRepository

class RepositoryFactory:
    def __init__(self):
        self.__user_repository = UserRepository()
        self.__order_repository = OrderRepository()
        self.__product_repository = ProductRepository()
        self.__discount_repository = DiscountRepository()
        self.__delivery_repository = DeliveryRepository()
    
    @property
    def user_repo(self):
        return self.__user_repository
    
    @property
    def product_repo(self):
        return self.__product_repository
    
    @property
    def order_repo(self):
        return self.__order_repository
    
    @property
    def discount_repo(self):
        return self.__discount_repository
    
    @property
    def delivery_repo(self):
        return self.__delivery_repository