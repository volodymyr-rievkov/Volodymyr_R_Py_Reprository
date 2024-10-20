import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_1.settings")
django.setup()

from app.repository_factory import RepositoryFactory

users_repo = RepositoryFactory.get_repository("User")
users_repo.show_all()

discounts_repo = RepositoryFactory.get_repository("Discount")
discounts_repo.show_all()

products_repo = RepositoryFactory.get_repository("Product")
products_repo.show_all()

orders_repo = RepositoryFactory.get_repository("Order")
orders_repo.show_all()

delivery_repo = RepositoryFactory.get_repository("Delivery")
delivery_repo.show_all()
