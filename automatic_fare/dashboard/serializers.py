from rest_framework import serializers
from django.contrib.auth.models import User
from .models import RFIDCard, Ride


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class RFIDCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFIDCard
        fields = ['id', 'card_id', 'balance']


class RideSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    end_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    class Meta:
        model = Ride
        fields = [
            'id',
            'start_latitude',
            'start_longitude',
            'end_latitude',
            'end_longitude',
            'start_time',
            'end_time',
            'fare',
            'ride_ended',
        ]
