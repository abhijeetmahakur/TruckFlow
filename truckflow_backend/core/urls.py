from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TruckViewSet, LoadViewSet, TripViewSet, BookingViewSet,
    ContactRecordViewSet, NotificationViewSet, ProofOfDeliveryViewSet,
    dashboard_stats, match_round_trip, route_coordinates,
    calculate_profit, book_round_trip
)

router = DefaultRouter()
router.register(r'trucks', TruckViewSet)
router.register(r'loads', LoadViewSet)
router.register(r'trips', TripViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'contacts', ContactRecordViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'pod', ProofOfDeliveryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-stats/', dashboard_stats, name='dashboard-stats'),
    path('match-round-trip/', match_round_trip, name='match-round-trip'),
    path('route-coordinates/', route_coordinates, name='route-coordinates'),
    path('calculate-profit/', calculate_profit, name='calculate-profit'),
    path('book-round-trip/', book_round_trip, name='book-round-trip'),
]
