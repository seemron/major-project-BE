from django.urls import path
from .views import AddBalanceView, RideView,CardListView, AddCardView, add_ride, UserLoginView, UserLogoutView,CardView,user_dashboard,register_user_and_card


from .views import LoginAPIView, ProfileAPIView, RechargeAPIView, RideDetailsAPIView

# app_name = 'dashboard'
urlpatterns = [
    path('', user_dashboard, name='card_list'),
    # path("", CardListView.as_view(), name="card_list"),
    path("add-card/", AddCardView.as_view(), name="add_card"),
    path("add-ride/<int:pk>/", add_ride, name="add_ride"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path('add-balance/', AddBalanceView.as_view(), name='add_balance'),
    path('ride/', RideView.as_view(), name='ride'),
    path('check-card/', CardView.as_view(), name='check_ride'),

    path('register/', register_user_and_card, name='register_user_and_card'),



    #API
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/profile/', ProfileAPIView.as_view(), name='profile'),
    path('api/recharge/', RechargeAPIView.as_view(), name='recharge'),
    path('api/rides/', RideDetailsAPIView.as_view(), name='rides'),
]
