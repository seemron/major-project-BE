from django.http import JsonResponse
from django.views import View
import json
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import RFIDCard, Ride
from .forms import RFIDCardForm, RideForm,RFIDCard, Ride
from django.contrib.auth.views import LoginView, LogoutView
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from decimal import Decimal

class UserLoginView(LoginView):
    template_name = "login.html"
    success_url= reverse_lazy("card_list")


@login_required
def user_dashboard(request):
    user = request.user
    rfid_cards = user.rfid_cards.all()  # Fetch all RFIDCards linked to the user
    if user.is_superuser:
        rfid_cards = RFIDCard.objects.all()  # Fetch all RFIDCards linked to the user
    context = {
        'user': user,
        'rfid_cards': rfid_cards,
    }
    return render(request, 'user_dashboard.html', context)



class UserLogoutView(LogoutView):
    next_page = reverse_lazy("card_list")

@method_decorator(csrf_exempt, name='dispatch')
class CardView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        card_id = data.get("card_id")
        print(card_id,"test123")
        card =RFIDCard.objects.filter(card_id=card_id)
        if not card:
            return JsonResponse({"message": "Card not registered.", "card": card_id}, status=404)
        else:
            return JsonResponse({"message": "Card registered.", "card": card_id}, status=200)

class AddBalanceView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        card_id = data.get("card_id")
        amount = data.get("amount")

        card = get_object_or_404(RFIDCard, card_id=card_id)
        card.balance += float(amount)
        card.save()
        return JsonResponse({"message": "Balance added", "new_balance": card.balance}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class RideView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        card_id = data.get("card_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        card =RFIDCard.objects.filter(card_id=card_id)
        if not card:
            return JsonResponse({"message": "Card not registered.", "card": card_id}, status=404)
        else:
            card = card.first()

        if card.balance < 20:
            return JsonResponse({"message": "Insufficient balance", "card": card.id}, status=200)
        
        previous_ride = Ride.objects.filter(card=card,ride_ended = False)
        
        if previous_ride:
            previous_ride = previous_ride.first()
            previous_ride.end_latitude = float(latitude)
            previous_ride.end_longitude = float(longitude)
            previous_ride.end_time = now()
            previous_ride.ride_ended = True
            previous_ride.fare = previous_ride.calculate_fare()
            previous_ride.deduct_fare()
            previous_ride.save()
            return JsonResponse({
                "message": "Ride ended",
                "fare": previous_ride.fare,
                "remaining_balance": card.balance
            }, status=200)

        ride = Ride.objects.create(
            card=card,
            start_latitude=float(latitude),
            start_longitude=float(longitude),
        )
        return JsonResponse({"message": "Ride started", "ride_id": ride.id}, status=201)


@method_decorator(login_required, name='dispatch')
class CardListView(ListView):
    model = RFIDCard
    template_name = "card_list.html"
    context_object_name = "cards"

@method_decorator(login_required, name='dispatch')
class AddCardView(CreateView):
    model = RFIDCard
    form_class = RFIDCardForm
    template_name = "add_card.html"
    success_url = reverse_lazy("card_list")

@login_required
def add_ride(request, pk):
    card = get_object_or_404(RFIDCard, pk=pk)
    if request.method == "POST":
        form = RideForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.card = card
            ride.save()
            return redirect("card_list")
    else:
        form = RideForm()
    return render(request, "add_ride.html", {"form": form, "card": card})

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegistrationForm, RFIDCardForm


def superadmin_required(user):
    return user.is_superuser

@user_passes_test(superadmin_required)
def register_user_and_card(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        card_form = RFIDCardForm(request.POST)
        if user_form.is_valid() and card_form.is_valid():
            # Save the user
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            # Assign the card to the user
            card = card_form.save(commit=False)
            card.user = user
            card.save()

            # Log the user in
            login(request, user)

            messages.success(request, "Registration successful!")
            return redirect('card_list')
    else:
        user_form = UserRegistrationForm()
        card_form = RFIDCardForm()

    context = {
        'user_form': user_form,
        'card_form': card_form,
    }
    return render(request, 'register_user_and_card.html', context)






#API

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import *
from rest_framework.permissions import IsAuthenticated

class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'message': 'Login successful'})
        return Response({'error': 'Invalid credentials'}, status=400)



class ProfileAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        rfid_cards = RFIDCard.objects.filter(user=user)
        user_data = UserSerializer(user).data
        rfid_data = RFIDCardSerializer(rfid_cards, many=True).data
        return Response({'user': user_data, 'rfid_cards': rfid_data})



class RechargeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        card_id = request.data.get('card_id')
        amount = request.data.get('amount')

        try:
            card = RFIDCard.objects.get(card_id=card_id, user=request.user)
            card.balance += Decimal(amount)
            card.save()
            return Response({'message': 'Recharge successful', 'new_balance': card.balance})
        except RFIDCard.DoesNotExist:
            return Response({'error': 'Card not found'}, status=404)



class RideDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rfid_cards = RFIDCard.objects.filter(user=request.user)
        rides = Ride.objects.filter(card__in=rfid_cards)
        rides_data = RideSerializer(rides, many=True).data
        return Response({'rides': rides_data})
