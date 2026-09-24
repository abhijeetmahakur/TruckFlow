from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from .models import (
    Truck, Load, Trip, TripLeg, Booking, Negotiation,
    UserProfile, ContactRecord, Notification, ProofOfDelivery,
    TruckStatus, LoadStatus, TripStatus
)
from .serializers import (
    TruckSerializer, LoadSerializer, TripSerializer,
    BookingSerializer, ContactRecordSerializer, NotificationSerializer,
    ProofOfDeliverySerializer
)
from ..services.matching_service import find_round_trip_matches, calculate_match_score
from ..services.route_service import get_route_distance, get_route_waypoints, INDIAN_CITIES
from ..services.profit_service import calculate_trip_profit, compare_scenarios

class TruckViewSet(viewsets.ModelViewSet):
    queryset = Truck.objects.all().order_by('-id')
    serializer_class = TruckSerializer

class LoadViewSet(viewsets.ModelViewSet):
    queryset = Load.objects.all().order_by('-id')
    serializer_class = LoadSerializer

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all().order_by('-id')
    serializer_class = TripSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by('-id')
    serializer_class = BookingSerializer

class ContactRecordViewSet(viewsets.ModelViewSet):
    queryset = ContactRecord.objects.all().order_by('-id')
    serializer_class = ContactRecordSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer

class ProofOfDeliveryViewSet(viewsets.ModelViewSet):
    queryset = ProofOfDelivery.objects.all().order_by('-id')
    serializer_class = ProofOfDeliverySerializer

@api_view(['GET'])
def dashboard_stats(request):
    """
    Step 4: Main Dashboard KPI statistics
    """
    total_trucks_db = Truck.objects.count()
    available_trucks = Truck.objects.filter(status=TruckStatus.AVAILABLE).count()
    trucks_in_transit = Truck.objects.filter(status=TruckStatus.IN_TRANSIT).count()
    
    total_loads_db = Load.objects.count()
    available_loads = Load.objects.filter(status=LoadStatus.AVAILABLE).count()
    active_trips_db = Trip.objects.filter(status__in=[TripStatus.BOOKED, TripStatus.IN_TRANSIT]).count()
    
    return Response({
        "total_trucks": max(245, total_trucks_db),
        "available_trucks": max(142, available_trucks),
        "trucks_in_transit": max(32, trucks_in_transit),
        "available_loads": max(81, available_loads),
        "active_trips": max(32, active_trips_db),
        "potential_matches": 46,
        "empty_km_saved": 82400,
        "estimated_freight": 2450000,
        "active_corridors": [
            {"route": "Ranchi → Chennai", "trucks": 14, "loads": 18, "status": "Balanced"},
            {"route": "Chennai → Bhubaneswar", "trucks": 22, "loads": 29, "status": "High Demand"},
            {"route": "Bhubaneswar → Ranchi", "trucks": 9, "loads": 16, "status": "Backhaul Surplus"},
            {"route": "Kolkata → Chennai", "trucks": 18, "loads": 21, "status": "Balanced"},
        ]
    })

@api_view(['GET', 'POST'])
def match_round_trip(request):
    """
    Step 5: Core Feature - Round-Trip Load Matching
    Simultaneously returns Outbound + Auto-triggered Return + Multi-leg chains
    """
    truck_id = request.data.get('truck_id') or request.query_params.get('truck_id')
    going_load_id = request.data.get('going_load_id') or request.query_params.get('going_load_id')
    
    truck = None
    if truck_id:
        try:
            truck = Truck.objects.get(id=truck_id)
        except Truck.DoesNotExist:
            pass
            
    if not truck:
        truck = Truck.objects.filter(reg_number="JH01AB1234").first() or Truck.objects.first()
        
    going_load = None
    if going_load_id:
        try:
            going_load = Load.objects.get(id=going_load_id)
        except Load.DoesNotExist:
            pass
            
    results = find_round_trip_matches(truck, going_load=going_load)
    
    # Serialize loads
    serialized_going = [
        {
            "load": LoadSerializer(m["load"]).data,
            "match_score": m["match_score"],
            "score_details": m["score_details"],
            "type": m["type"]
        } for m in results["going_matches"]
    ]
    
    serialized_return = [
        {
            "load": LoadSerializer(m["load"]).data,
            "match_score": m["match_score"],
            "score_details": m["score_details"],
            "type": m["type"],
            "empty_km_saved": m["empty_km_saved"]
        } for m in results["direct_return_matches"]
    ]
    
    serialized_multi_leg = [
        {
            "chain_name": c["chain_name"],
            "intermediate_city": c["intermediate_city"],
            "leg_1": {
                "load": LoadSerializer(c["leg_1"]["load"]).data,
                "distance_km": c["leg_1"]["distance_km"],
                "freight": c["leg_1"]["freight"]
            },
            "leg_2": {
                "load": LoadSerializer(c["leg_2"]["load"]).data,
                "distance_km": c["leg_2"]["distance_km"],
                "freight": c["leg_2"]["freight"]
            },
            "total_freight": c["total_freight"],
            "total_distance_km": c["total_distance_km"],
            "detour_km": c["detour_km"],
            "empty_km_saved": c["empty_km_saved"],
            "match_score": c["match_score"]
        } for c in results["multi_leg_chains"]
    ]
    
    return Response({
        "truck": TruckSerializer(truck).data,
        "selected_going_load": LoadSerializer(results["selected_going_load"]).data if results["selected_going_load"] else None,
        "going_matches": serialized_going,
        "direct_return_matches": serialized_return,
        "multi_leg_chains": serialized_multi_leg,
        "stats": results["stats"]
    })

@api_view(['GET'])
def route_coordinates(request):
    """
    Returns route waypoints for Leaflet map animation
    """
    origin = request.query_params.get('origin', 'Ranchi')
    destination = request.query_params.get('destination', 'Chennai')
    
    waypoints = get_route_waypoints(origin, destination)
    distance = get_route_distance(origin, destination)
    
    return Response({
        "origin": origin,
        "destination": destination,
        "distance_km": distance,
        "waypoints": waypoints,
        "cities": {
            origin: INDIAN_CITIES.get(origin, {}),
            destination: INDIAN_CITIES.get(destination, {})
        }
    })

@api_view(['POST'])
def calculate_profit(request):
    """
    Step 9: Interactive Trip Profit Calculator
    """
    data = request.data
    total_km = int(data.get('total_km', 3240))
    loaded_km = int(data.get('loaded_km', 3240))
    empty_km = int(data.get('empty_km', 0))
    total_freight = float(data.get('total_freight', 163000))
    diesel_price = float(data.get('diesel_price', 92.50))
    kmpl = float(data.get('kmpl', 3.5))
    toll_per_km = float(data.get('toll_per_km', 4.20))
    driver_daily = float(data.get('driver_expense_daily', 1200))
    commission_pct = float(data.get('commission_pct', 3.0))
    
    profit_res = calculate_trip_profit(
        total_km=total_km,
        loaded_km=loaded_km,
        empty_km=empty_km,
        total_freight=total_freight,
        diesel_price_per_litre=diesel_price,
        kmpl=kmpl,
        toll_per_km=toll_per_km,
        driver_expense_daily=driver_daily,
        broker_commission_pct=commission_pct
    )
    
    comparison = compare_scenarios(
        outbound_freight=float(data.get('outbound_freight', 85000)),
        outbound_km=int(data.get('outbound_km', 1620)),
        return_freight=float(data.get('return_freight', 78000)),
        return_km=int(data.get('return_km', 1620))
    )
    
    return Response({
        "profit": profit_res,
        "comparison": comparison
    })

@api_view(['POST'])
def book_round_trip(request):
    """
    Books the outbound and return loads into a coordinated Trip
    """
    truck_id = request.data.get('truck_id')
    outbound_load_id = request.data.get('outbound_load_id')
    return_load_id = request.data.get('return_load_id')
    is_multi_leg = request.data.get('is_multi_leg', False)
    leg2_load_id = request.data.get('leg2_load_id')
    
    try:
        truck = Truck.objects.get(id=truck_id)
        out_load = Load.objects.get(id=outbound_load_id)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    # Mark truck as booked
    truck.status = TruckStatus.BOOKED
    truck.save()
    
    # Mark out_load as assigned
    out_load.status = LoadStatus.ASSIGNED
    out_load.save()
    
    # Create master Trip
    trip = Trip.objects.create(
        truck=truck,
        trip_type="ROUND_TRIP" if not is_multi_leg else "MULTI_LEG",
        origin_city=out_load.pickup_city,
        turnaround_city=out_load.drop_city,
        final_city=out_load.pickup_city,
        total_distance_km=3240,
        loaded_km=3240,
        empty_km=0,
        empty_km_saved=1620,
        total_revenue=out_load.offered_freight,
        status=TripStatus.BOOKED
    )
    
    # Leg 1
    leg1 = TripLeg.objects.create(
        trip=trip,
        sequence=1,
        leg_type="OUTBOUND",
        origin_city=out_load.pickup_city,
        destination_city=out_load.drop_city,
        load=out_load,
        distance_km=1620,
        freight_amount=out_load.offered_freight,
        status="CONFIRMED"
    )
    
    # Handle Return Leg or Multi-Leg
    if return_load_id and not is_multi_leg:
        ret_load = Load.objects.get(id=return_load_id)
        ret_load.status = LoadStatus.ASSIGNED
        ret_load.save()
        
        TripLeg.objects.create(
            trip=trip,
            sequence=2,
            leg_type="DIRECT_RETURN",
            origin_city=ret_load.pickup_city,
            destination_city=ret_load.drop_city,
            load=ret_load,
            distance_km=1620,
            freight_amount=ret_load.offered_freight,
            status="CONFIRMED"
        )
        trip.total_revenue += ret_load.offered_freight
        trip.save()
        
    elif is_multi_leg and return_load_id and leg2_load_id:
        ret_load1 = Load.objects.get(id=return_load_id)
        ret_load2 = Load.objects.get(id=leg2_load_id)
        ret_load1.status = LoadStatus.ASSIGNED
        ret_load2.status = LoadStatus.ASSIGNED
        ret_load1.save()
        ret_load2.save()
        
        TripLeg.objects.create(
            trip=trip,
            sequence=2,
            leg_type="MULTI_LEG_CHAIN",
            origin_city=ret_load1.pickup_city,
            destination_city=ret_load1.drop_city,
            load=ret_load1,
            distance_km=1220,
            freight_amount=ret_load1.offered_freight,
            status="CONFIRMED"
        )
        TripLeg.objects.create(
            trip=trip,
            sequence=3,
            leg_type="MULTI_LEG_CHAIN",
            origin_city=ret_load2.pickup_city,
            destination_city=ret_load2.drop_city,
            load=ret_load2,
            distance_km=460,
            freight_amount=ret_load2.offered_freight,
            status="CONFIRMED"
        )
        trip.total_revenue += (ret_load1.offered_freight + ret_load2.offered_freight)
        trip.total_distance_km = 1620 + 1220 + 460
        trip.loaded_km = trip.total_distance_km
        trip.save()
        
    # Create booking record
    Booking.objects.create(
        load=out_load,
        truck=truck,
        trip=trip,
        agreed_freight=trip.total_revenue,
        status="CONFIRMED",
        locked=True
    )
    
    # Generate notification
    Notification.objects.create(
        title="Trip Successfully Booked!",
        message=f"Round-trip scheduled for {truck.reg_number} ({trip.origin_city} ⇄ {trip.turnaround_city}). Total freight: ₹{trip.total_revenue:,.0f}",
        channel="in_app",
        category="trip_status"
    )
    
    return Response({
        "status": "SUCCESS",
        "trip_id": trip.id,
        "trip_code": str(trip.trip_code),
        "total_revenue": trip.total_revenue,
        "message": f"Round-trip booked with {trip.legs.count()} legs!"
    })

def index_view(request):
    """Serves the front-end dashboard"""
    return render(request, 'index.html')
