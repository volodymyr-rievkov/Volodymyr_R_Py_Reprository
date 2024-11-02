from app.models.order import Order

from rest_framework import serializers

class OrderSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        model = Order
        fields = '__all__'