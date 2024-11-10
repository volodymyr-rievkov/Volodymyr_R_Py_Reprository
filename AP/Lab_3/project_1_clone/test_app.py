import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_1.settings")
django.setup()

from app.repository_factory import RepositoryFactory

repo_factory = RepositoryFactory()
repo_factory.user_repo.show_all()
repo_factory.product_repo.show_all()
repo_factory.order_repo.show_all()
repo_factory.discount_repo.show_all()
repo_factory.delivery_repo.show_all()
