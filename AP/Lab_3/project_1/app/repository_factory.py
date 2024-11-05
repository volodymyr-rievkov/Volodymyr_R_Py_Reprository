from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.discount_repository import DiscountRepository
from app.repositories.delivery_repository import DeliveryRepository

class RepositoryFactory:

    __USER_REPOSITORY = UserRepository()
    __PRODUCT_REPOSITORY = ProductRepository()
    __ORDER_REPOSITORY = OrderRepository()
    __DISCOUNT_REPOSITORY = DiscountRepository()
    __DELIVERY_REPOSITORY = DeliveryRepository()

    @classmethod
    def user_repo(cls):
        return cls.__USER_REPOSITORY
    
    @classmethod
    def product_repo(cls):
        return cls.__PRODUCT_REPOSITORY
    
    @classmethod
    def order_repo(cls):
        return cls.__ORDER_REPOSITORY
    
    @classmethod
    def discount_repo(cls):
        return cls.__DISCOUNT_REPOSITORY
    
    @classmethod
    def delivery_repo(cls):
        return cls.__DELIVERY_REPOSITORY