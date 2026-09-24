from rest_framework import serializers
from .models import (
    Truck, Load, Trip, TripLeg, Booking, Negotiation,
    UserProfile, ContactRecord, Notification, ProofOfDelivery
)

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = UserProfile
        fields = '__all__'

class TruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Truck
        fields = '__all__'

class LoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Load
        fields = '__all__'

class TripLegSerializer(serializers.ModelSerializer):
    load_details = LoadSerializer(source='load', read_only=True)
    class Meta:
        model = TripLeg
        fields = '__all__'

class TripSerializer(serializers.ModelSerializer):
    truck_details = TruckSerializer(source='truck', read_only=True)
    legs = TripLegSerializer(many=True, read_only=True)
    class Meta:
        model = Trip
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    load_details = LoadSerializer(source='load', read_only=True)
    truck_details = TruckSerializer(source='truck', read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'

class ContactRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRecord
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class ProofOfDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProofOfDelivery
        fields = '__all__'
