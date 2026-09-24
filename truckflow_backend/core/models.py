import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class RoleChoice(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    BROKER = 'BROKER', 'Freight Broker'
    TRUCK_OWNER = 'TRUCK_OWNER', 'Fleet / Truck Owner'
    DRIVER = 'DRIVER', 'Truck Driver'
    SHIPPER = 'SHIPPER', 'Company / Shipper'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=RoleChoice.choices, default=RoleChoice.BROKER)
    phone = models.CharField(max_length=15, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_badge = models.CharField(max_length=50, default='Unverified')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.8)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

class TruckStatus(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    BOOKED = 'BOOKED', 'Booked'
    LOADING = 'LOADING', 'Loading'
    IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
    UNLOADING = 'UNLOADING', 'Unloading'
    LOOKING_FOR_RETURN = 'LOOKING_FOR_RETURN', 'Looking for Return Load'
    MAINTENANCE = 'MAINTENANCE', 'Maintenance'
    OFFLINE = 'OFFLINE', 'Offline'

class Truck(models.Model):
    reg_number = models.CharField(max_length=20, unique=True, help_text="e.g. JH01AB1234")
    model_name = models.CharField(max_length=80, default="Tata Prima 5530.S")
    truck_type = models.CharField(max_length=50, default="Multi-Axle Semi Trailer")
    body_type = models.CharField(max_length=50, default="Closed Container 40ft")
    capacity_tons = models.DecimalField(max_digits=6, decimal_places=2, default=25.0)
    volume_cu_ft = models.IntegerField(default=1800)
    
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_trucks')
    owner_name = models.CharField(max_length=100, default="Rajesh Transport Corp")
    driver_name = models.CharField(max_length=100, default="Suresh Kumar")
    driver_phone = models.CharField(max_length=20, default="+91 98765 43210")
    driver_photo_url = models.CharField(max_length=255, blank=True)
    
    base_location = models.CharField(max_length=100, default="Ranchi, Jharkhand")
    current_location = models.CharField(max_length=100, default="Ranchi, Jharkhand")
    current_destination = models.CharField(max_length=100, default="Chennai, Tamil Nadu")
    current_lat = models.FloatField(default=23.3441)
    current_lng = models.FloatField(default=85.3096)
    
    availability_date = models.DateField(default=timezone.now)
    preferred_routes = models.TextField(default="Ranchi-Chennai, Chennai-Kolkata, Chennai-Ranchi")
    status = models.CharField(max_length=30, choices=TruckStatus.choices, default=TruckStatus.AVAILABLE)
    
    insurance_expiry = models.DateField(null=True, blank=True)
    fitness_expiry = models.DateField(null=True, blank=True)
    permit_info = models.CharField(max_length=100, default="All India National Permit (NP)")
    
    fuel_efficiency_kmpl = models.DecimalField(max_digits=4, decimal_places=2, default=3.5)
    odometer_km = models.IntegerField(default=142500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reg_number} ({self.capacity_tons}T, {self.current_location})"

class LoadStatus(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    RESERVED = 'RESERVED', 'Reserved'
    ASSIGNED = 'ASSIGNED', 'Assigned'
    LOADING = 'LOADING', 'Loading'
    IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'

class Load(models.Model):
    load_code = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
    company_name = models.CharField(max_length=100, default="Tata Steel BSL / Jindal")
    shipper = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='posted_loads')
    
    pickup_city = models.CharField(max_length=50)
    pickup_state = models.CharField(max_length=50)
    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    
    drop_city = models.CharField(max_length=50)
    drop_state = models.CharField(max_length=50)
    drop_lat = models.FloatField()
    drop_lng = models.FloatField()
    
    weight_tons = models.DecimalField(max_digits=6, decimal_places=2)
    goods_type = models.CharField(max_length=100, default="Steel Products")
    required_truck_type = models.CharField(max_length=50, default="Multi-Axle Semi Trailer")
    
    pickup_date = models.DateField(default=timezone.now)
    delivery_deadline = models.DateField(null=True, blank=True)
    offered_freight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total Freight in INR (₹)")
    market_benchmark_freight = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    loading_instructions = models.TextField(blank=True, default="Standard warehouse loading dock; require tarp and securing chains.")
    special_requirements = models.CharField(max_length=200, blank=True, default="Over-dimensional permit not required")
    status = models.CharField(max_length=30, choices=LoadStatus.choices, default=LoadStatus.AVAILABLE)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.load_code}: {self.pickup_city} → {self.drop_city} ({self.weight_tons}T, ₹{self.offered_freight:,.0f})"

class TripStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft Proposal'
    BOOKED = 'BOOKED', 'Booked'
    LOADING = 'LOADING', 'Loading'
    IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
    UNLOADING = 'UNLOADING', 'Unloading'
    DELIVERED = 'DELIVERED', 'Delivered'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'

class Trip(models.Model):
    trip_code = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, related_name='trips')
    broker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_trips')
    
    trip_type = models.CharField(max_length=30, default="ROUND_TRIP", help_text="ONE_WAY, ROUND_TRIP, or MULTI_LEG")
    origin_city = models.CharField(max_length=50, default="Ranchi")
    turnaround_city = models.CharField(max_length=50, default="Chennai")
    final_city = models.CharField(max_length=50, default="Ranchi")
    
    total_distance_km = models.IntegerField(default=3240)
    loaded_km = models.IntegerField(default=3240)
    empty_km = models.IntegerField(default=0)
    empty_km_saved = models.IntegerField(default=1620)
    
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    estimated_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    estimated_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    
    status = models.CharField(max_length=30, choices=TripStatus.choices, default=TripStatus.BOOKED)
    current_leg_index = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trip {self.trip_code} - {self.truck.reg_number} ({self.origin_city} ⇄ {self.turnaround_city})"

class TripLeg(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='legs')
    sequence = models.IntegerField(default=1)
    leg_type = models.CharField(max_length=30, default="OUTBOUND", help_text="OUTBOUND, DIRECT_RETURN, or MULTI_LEG_CHAIN")
    
    origin_city = models.CharField(max_length=50)
    destination_city = models.CharField(max_length=50)
    load = models.ForeignKey(Load, on_delete=models.SET_NULL, null=True, blank=True, related_name='trip_legs')
    
    distance_km = models.IntegerField(default=1620)
    freight_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=30, default="PENDING")
    
    def __str__(self):
        return f"Leg {self.sequence}: {self.origin_city} → {self.destination_city} (₹{self.freight_amount:,.0f})"

class Booking(models.Model):
    booking_id = models.CharField(max_length=30, unique=True, default=uuid.uuid4)
    load = models.ForeignKey(Load, on_delete=models.CASCADE, related_name='bookings')
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, related_name='bookings')
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    agreed_freight = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=30, default="CONFIRMED")
    locked = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.booking_id} - {self.load.load_code} on {self.truck.reg_number}"

class Negotiation(models.Model):
    load = models.ForeignKey(Load, on_delete=models.CASCADE, related_name='negotiations')
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, related_name='negotiations')
    proposer = models.ForeignKey(User, on_delete=models.CASCADE)
    proposed_freight = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='PENDING')  # PENDING, ACCEPTED, REJECTED, COUNTERED
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ProofOfDelivery(models.Model):
    trip_leg = models.OneToOneField(TripLeg, on_delete=models.CASCADE, related_name='pod')
    lr_number = models.CharField(max_length=50, default="LR-2026-9812")
    document_image = models.CharField(max_length=255, blank=True)
    signature_data = models.TextField(blank=True, help_text="Base64 digital signature")
    delivered_at = models.DateTimeField(default=timezone.now)
    delivery_lat = models.FloatField(default=13.0827)
    delivery_lng = models.FloatField(default=80.2707)
    verified = models.BooleanField(default=True)

class ContactRecord(models.Model):
    CONTACT_TYPES = [
        ('TRUCK_OWNER', 'Truck Owner'),
        ('DRIVER', 'Driver'),
        ('SHIPPER', 'Shipper / Company'),
        ('TRANSPORTER', 'Transporter'),
    ]
    name = models.CharField(max_length=100)
    contact_type = models.CharField(max_length=30, choices=CONTACT_TYPES)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    company = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100)
    preferred_routes = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.8)
    total_trips = models.IntegerField(default=12)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_contact_type_display()}) - {self.location}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=120)
    message = models.TextField()
    channel = models.CharField(max_length=20, default='in_app') # in_app, whatsapp, sms
    category = models.CharField(max_length=30, default='match_alert') # match_alert, trip_status, document_expiry
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    action = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
