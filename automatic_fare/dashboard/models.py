from django.db import models
from django.utils.timezone import now
from math import radians, sin, cos, sqrt, atan2
from decimal import Decimal
from django.contrib.auth.models import User

class RFIDCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True, related_name="rfid_cards")
    card_id = models.CharField(max_length=50, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.card_id

class Ride(models.Model):
    card = models.ForeignKey(RFIDCard, on_delete=models.CASCADE, related_name="rides")
    start_latitude = models.FloatField()
    start_longitude = models.FloatField()
    end_latitude = models.FloatField(null=True, blank=True)
    end_longitude = models.FloatField(null=True, blank=True)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(null=True, blank=True)
    fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ride_ended = models.BooleanField(default=False, blank=True)
    def calculate_distance(self):
        if self.end_latitude is None or self.end_longitude is None:
            return 0
        # Haversine formula for distance calculation
        R = 6371  # Earth radius in kilometers
        lat1, lon1 = radians(self.start_latitude), radians(self.start_longitude)
        lat2, lon2 = radians(self.end_latitude), radians(self.end_longitude)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        return distance

    def calculate_fare(self, rate_per_km=10):
        distance = self.calculate_distance()
        return distance * rate_per_km

    def deduct_fare(self):
        if self.fare is not None :
            self.card.balance -= Decimal(self.fare)
            self.card.save()

    def __str__(self):
        return f"Ride for Card: {self.card.card_id}"
