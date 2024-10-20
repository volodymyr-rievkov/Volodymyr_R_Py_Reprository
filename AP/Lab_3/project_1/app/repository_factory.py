from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.discount_repository import DiscountRepository
from app.repositories.delivery_repository import DeliveryRepository

class RepositoryFactory:
    @staticmethod
    def get_repository(repo_type):

        if (repo_type == "User"):
            return UserRepository()
        elif (repo_type == "Product"):
            return ProductRepository()
        elif (repo_type == "Order"):
            return OrderRepository()
        elif (repo_type == "Discount"):
            return DiscountRepository()
        elif (repo_type == "Delivery"):
            return DeliveryRepository()
        else:
            print(f"Error: Unknown repository type: {repo_type}.")
        