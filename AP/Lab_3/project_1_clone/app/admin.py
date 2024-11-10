from django.contrib import admin
from app.models.delivery import Delivery
from app.models.discount import Discount
from app.models.user import User
from app.models.product import Product
from app.models.order import Order


admin.site.register(Discount)
admin.site.register(Order)
admin.site.register(User)
admin.site.register(Delivery)
admin.site.register(Product)
