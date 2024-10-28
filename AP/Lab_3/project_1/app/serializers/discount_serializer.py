from app.models.discount import Discount
from rest_framework import serializers

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'