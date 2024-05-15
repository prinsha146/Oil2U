from rest_framework import serializers
from .models import Customer, Order, Invoice, Maintainence, UrgentDelivery, Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
       model = Customer
       fields= "__all__"
    
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()
       

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
class UpdateUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Customer
        fields = ['first_name','last_name','company_name','address', 'phone_number', 'email', ]
        disallowed = ['password', ]
    
    def update(self, instance, validated_data):

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.company_name = validated_data.get('company_name', instance.company_name)
        instance.address = validated_data.get('address', instance.address)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.email = validated_data.get('email', instance.email)
        if validated_data.get("password") is None:
            instance.password = validated_data.get('password', instance.password)
        instance.save()
        return instance


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        

class InvoiceInputSerializer(serializers.Serializer):
    ORDER_CHOICES = [
        ('scheduled', 'scheduled'),
        ('urgent', 'urgent'),
    ]
    type = serializers.ChoiceField(choices=ORDER_CHOICES)
    order_id = serializers.IntegerField()

        

class MaintainenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintainence
        fields = "__all__"
        

class UrgentDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = UrgentDelivery
        fields = "__all__"
        

class InvoiceSerializer(serializers.ModelSerializer):
    order = OrderSerializer()  # Assuming OrderSerializer is defined
    urgent_delivery = UrgentDeliverySerializer()  
    class Meta:
        model = Invoice
        fields = "__all__"
        depth = 2


class NotificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Notification
        fields = "__all__"
        
    