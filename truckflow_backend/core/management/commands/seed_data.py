import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from truckflow_backend.core.models import (
    UserProfile, RoleChoice, Truck, Load, TruckStatus, LoadStatus,
    ContactRecord, Notification
)

class Command(BaseCommand):
    help = 'Seeds realistic demo data specified in Step 26 of TruckFlow build prompt'

    def handle(self, *args, **options):
        self.stdout.write("Seeding TruckFlow demo database...")

        # 1. Create or get Demo Users
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@truckflow.in'})
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'role': RoleChoice.ADMIN, 'phone': '+91 98111 00001', 'company_name': 'TruckFlow HQ', 'is_verified': True, 'verification_badge': 'Platform Admin'}
        )

        broker_user, _ = User.objects.get_or_create(username='broker_rajesh', defaults={'email': 'broker@truckflow.in', 'first_name': 'Rajesh', 'last_name': 'Sharma'})
        broker_user.set_password('broker123')
        broker_user.save()
        UserProfile.objects.get_or_create(
            user=broker_user,
            defaults={'role': RoleChoice.BROKER, 'phone': '+91 98222 11112', 'company_name': 'Apex Freight Brokers', 'is_verified': True, 'verification_badge': 'Gold Broker Verified'}
        )

        owner_user, _ = User.objects.get_or_create(username='owner_vikram', defaults={'email': 'vikram@transport.in', 'first_name': 'Vikram', 'last_name': 'Singh'})
        owner_user.set_password('owner123')
        owner_user.save()
        UserProfile.objects.get_or_create(
            user=owner_user,
            defaults={'role': RoleChoice.TRUCK_OWNER, 'phone': '+91 98333 22223', 'company_name': 'Chotanagpur Roadlines', 'is_verified': True, 'verification_badge': 'Verified Fleet Owner'}
        )

        driver_user, _ = User.objects.get_or_create(username='driver_suresh', defaults={'email': 'suresh@driver.in', 'first_name': 'Suresh', 'last_name': 'Kumar'})
        driver_user.set_password('driver123')
        driver_user.save()
        UserProfile.objects.get_or_create(
            user=driver_user,
            defaults={'role': RoleChoice.DRIVER, 'phone': '+91 98765 43210', 'company_name': 'Independent Heavy Driver', 'is_verified': True, 'verification_badge': 'FastTrack Verified Driver'}
        )

        shipper_user, _ = User.objects.get_or_create(username='shipper_tata', defaults={'email': 'freight@tatabsl.com', 'first_name': 'Tata', 'last_name': 'Steel BSL'})
        shipper_user.set_password('shipper123')
        shipper_user.save()
        UserProfile.objects.get_or_create(
            user=shipper_user,
            defaults={'role': RoleChoice.SHIPPER, 'phone': '+91 98444 33334', 'company_name': 'Tata Steel BSL', 'is_verified': True, 'verification_badge': 'Enterprise Shipper'}
        )

        # 2. Clear existing demo trucks and loads
        Truck.objects.all().delete()
        Load.objects.all().delete()

        # 3. Create Step 26 Demo Trucks
        truck_jh = Truck.objects.create(
            reg_number="JH01AB1234",
            model_name="Tata Prima 5530.S Trailer",
            truck_type="Multi-Axle Semi Trailer",
            body_type="Closed Container 40ft",
            capacity_tons=25.0,
            volume_cu_ft=1800,
            owner=owner_user,
            owner_name="Chotanagpur Roadlines (Vikram Singh)",
            driver_name="Suresh Kumar",
            driver_phone="+91 98765 43210",
            base_location="Ranchi, Jharkhand",
            current_location="Ranchi, Jharkhand",
            current_destination="Chennai, Tamil Nadu",
            current_lat=23.3441,
            current_lng=85.3096,
            availability_date=datetime.date.today(),
            preferred_routes="Ranchi → Chennai, Chennai → Bhubaneswar → Ranchi",
            status=TruckStatus.AVAILABLE,
            permit_info="All India National Permit (NP)",
            fuel_efficiency_kmpl=3.5,
            odometer_km=142850
        )

        truck_od = Truck.objects.create(
            reg_number="OD02CD5678",
            model_name="Ashok Leyland 4220 HG",
            truck_type="Multi-Axle Heavy Truck",
            body_type="High Side Open Body",
            capacity_tons=20.0,
            volume_cu_ft=1450,
            owner_name="Kalinga Logistics Corp",
            driver_name="Bikram Nayak",
            driver_phone="+91 97788 12345",
            base_location="Chennai, Tamil Nadu",
            current_location="Chennai, Tamil Nadu",
            current_destination="Bhubaneswar, Odisha",
            current_lat=13.0827,
            current_lng=80.2707,
            availability_date=datetime.date.today(),
            preferred_routes="Chennai → Bhubaneswar, Bhubaneswar → Kolkata",
            status=TruckStatus.AVAILABLE,
            permit_info="All India National Permit (NP)",
            fuel_efficiency_kmpl=3.8,
            odometer_km=98400
        )

        truck_tn = Truck.objects.create(
            reg_number="TN09XY9988",
            model_name="BharatBenz 3528C Heavy Hauler",
            truck_type="Multi-Axle Heavy Hauler",
            body_type="Flatbed Heavy Platform",
            capacity_tons=28.0,
            volume_cu_ft=2000,
            owner_name="Coromandel Freight Fleet",
            driver_name="M. Selvam",
            driver_phone="+91 94441 55566",
            base_location="Chennai, Tamil Nadu",
            current_location="Chennai, Tamil Nadu",
            current_destination="Hyderabad, Telangana",
            current_lat=13.0827,
            current_lng=80.2707,
            availability_date=datetime.date.today(),
            preferred_routes="Chennai → Hyderabad, Hyderabad → Bangalore",
            status=TruckStatus.IN_TRANSIT,
            fuel_efficiency_kmpl=3.2,
            odometer_km=165200
        )

        truck_wb = Truck.objects.create(
            reg_number="WB11EF4321",
            model_name="Eicher Pro 6028",
            truck_type="Medium Axle Commercial",
            body_type="Closed Container 24ft",
            capacity_tons=16.0,
            volume_cu_ft=1100,
            owner_name="Howrah Freight Carrier",
            driver_name="Debabrata Roy",
            driver_phone="+91 93330 77788",
            base_location="Kolkata, West Bengal",
            current_location="Kolkata, West Bengal",
            current_destination="Ranchi, Jharkhand",
            current_lat=22.5726,
            current_lng=88.3639,
            availability_date=datetime.date.today(),
            preferred_routes="Kolkata → Ranchi → Jamshedpur",
            status=TruckStatus.AVAILABLE,
            fuel_efficiency_kmpl=4.2,
            odometer_km=76300
        )

        # 4. Create Step 26 Demo Loads
        load1 = Load.objects.create(
            load_code="LOAD-001",
            company_name="Tata Steel BSL / Bokaro Steel",
            shipper=shipper_user,
            pickup_city="Ranchi",
            pickup_state="Jharkhand",
            pickup_lat=23.3441,
            pickup_lng=85.3096,
            drop_city="Chennai",
            drop_state="Tamil Nadu",
            drop_lat=13.0827,
            drop_lng=80.2707,
            weight_tons=20.0,
            goods_type="Steel Coils & Heavy Sheets",
            required_truck_type="Multi-Axle Semi Trailer",
            pickup_date=datetime.date.today(),
            delivery_deadline=datetime.date.today() + datetime.timedelta(days=4),
            offered_freight=85000.0,
            market_benchmark_freight=82000.0,
            loading_instructions="Overhead gantry crane loading. Chains and anti-skid rubber pads required.",
            status=LoadStatus.AVAILABLE
        )

        load2 = Load.objects.create(
            load_code="LOAD-002",
            company_name="Hyundai Mobis / TVS Motor Spares",
            shipper=shipper_user,
            pickup_city="Chennai",
            pickup_state="Tamil Nadu",
            pickup_lat=13.0827,
            pickup_lng=80.2707,
            drop_city="Ranchi",
            drop_state="Jharkhand",
            drop_lat=23.3441,
            drop_lng=85.3096,
            weight_tons=18.0,
            goods_type="Automotive Components & Engine Spares",
            required_truck_type="Multi-Axle Semi Trailer",
            pickup_date=datetime.date.today() + datetime.timedelta(days=4),
            delivery_deadline=datetime.date.today() + datetime.timedelta(days=8),
            offered_freight=78000.0,
            market_benchmark_freight=75000.0,
            loading_instructions="High value palletized auto parts. Clean water-tight container mandatory.",
            status=LoadStatus.AVAILABLE
        )

        load3 = Load.objects.create(
            load_code="LOAD-003",
            company_name="Coromandel Fertilisers & Agri-Chem",
            shipper=shipper_user,
            pickup_city="Chennai",
            pickup_state="Tamil Nadu",
            pickup_lat=13.0827,
            pickup_lng=80.2707,
            drop_city="Bhubaneswar",
            drop_state="Odisha",
            drop_lat=20.2961,
            drop_lng=85.8245,
            weight_tons=15.0,
            goods_type="Agri Inputs & Packaged Consumer Goods",
            required_truck_type="Multi-Axle Heavy Truck",
            pickup_date=datetime.date.today() + datetime.timedelta(days=4),
            delivery_deadline=datetime.date.today() + datetime.timedelta(days=7),
            offered_freight=48000.0,
            market_benchmark_freight=46000.0,
            loading_instructions="Palletized bags; forklift loading at Ennore warehouse.",
            status=LoadStatus.AVAILABLE
        )

        load4 = Load.objects.create(
            load_code="LOAD-004",
            company_name="NALCO / Vedanta Smelter Auxiliaries",
            shipper=shipper_user,
            pickup_city="Bhubaneswar",
            pickup_state="Odisha",
            pickup_lat=20.2961,
            pickup_lng=85.8245,
            drop_city="Ranchi",
            drop_state="Jharkhand",
            drop_lat=23.3441,
            drop_lng=85.3096,
            weight_tons=12.0,
            goods_type="Industrial Raw Minerals & Refractory Bricks",
            required_truck_type="Multi-Axle Heavy Truck",
            pickup_date=datetime.date.today() + datetime.timedelta(days=7),
            delivery_deadline=datetime.date.today() + datetime.timedelta(days=9),
            offered_freight=34000.0,
            market_benchmark_freight=32000.0,
            loading_instructions="Crated refractory supplies; standard side loading.",
            status=LoadStatus.AVAILABLE
        )

        # Additional realistic loads for active marketplace
        Load.objects.create(
            load_code="LOAD-005",
            company_name="Jindal Steel & Power Ltd",
            pickup_city="Ranchi",
            pickup_state="Jharkhand",
            pickup_lat=23.3441,
            pickup_lng=85.3096,
            drop_city="Kolkata",
            drop_state="West Bengal",
            drop_lat=22.5726,
            drop_lng=88.3639,
            weight_tons=22.0,
            goods_type="Structural TMT Bars",
            required_truck_type="Multi-Axle Semi Trailer",
            pickup_date=datetime.date.today(),
            delivery_deadline=datetime.date.today() + datetime.timedelta(days=2),
            offered_freight=36000.0,
            market_benchmark_freight=35000.0,
            status=LoadStatus.AVAILABLE
        )

        Load.objects.create(
            load_code="LOAD-006",
            company_name="Ashok Leyland Ennore Works",
            pickup_city="Chennai",
            pickup_state="Tamil Nadu",
            pickup_lat=13.0827,
            pickup_lng=80.2707,
            drop_city="Hyderabad",
            drop_state="Telangana",
            drop_lat=17.3850,
            drop_lng=78.4867,
            weight_tons=16.0,
            goods_type="Commercial Vehicle Axles & Chassis Castings",
            required_truck_type="Multi-Axle Semi Trailer",
            pickup_date=datetime.date.today() + datetime.timedelta(days=2),
            delivery_deadline=datetime.date.today() + datetime.timedelta(days=4),
            offered_freight=42000.0,
            market_benchmark_freight=40000.0,
            status=LoadStatus.AVAILABLE
        )

        # 5. Seed CRM contacts for Step 11
        ContactRecord.objects.all().delete()
        ContactRecord.objects.create(
            name="Vikram Singh",
            contact_type="TRUCK_OWNER",
            phone="+91 98333 22223",
            company="Chotanagpur Roadlines",
            location="Ranchi, Jharkhand",
            preferred_routes="Ranchi ⇄ Chennai, Ranchi ⇄ Kolkata",
            notes="Has 8 multi-axle trailers (25-35T). Very reliable driver fleet. Prefers return freight contracts.",
            rating=4.9,
            total_trips=28
        )
        ContactRecord.objects.create(
            name="Suresh Kumar",
            contact_type="DRIVER",
            phone="+91 98765 43210",
            company="Chotanagpur Roadlines",
            location="Ranchi, Jharkhand",
            preferred_routes="NH-16 Coastal Highway Corridor",
            notes="12 years heavy trailer experience. Speaks Hindi and Odia fluently. Smartphone equipped with GPS.",
            rating=4.95,
            total_trips=42
        )
        ContactRecord.objects.create(
            name="Bikram Nayak",
            contact_type="DRIVER",
            phone="+91 97788 12345",
            company="Kalinga Logistics Corp",
            location="Bhubaneswar, Odisha",
            preferred_routes="Chennai ⇄ Bhubaneswar",
            notes="Specialist in container and FMCG movements along NH16.",
            rating=4.8,
            total_trips=31
        )
        ContactRecord.objects.create(
            name="Tata Steel BSL Logistics Desk",
            contact_type="SHIPPER",
            phone="+91 98444 33334",
            company="Tata Steel BSL",
            location="Jamshedpur / Ranchi",
            preferred_routes="Eastern to Southern corridors",
            notes="Regular outbound steel loads to Chennai and Bangalore. Timely payment on LR submission.",
            rating=4.85,
            total_trips=110
        )

        # 6. Seed Notifications
        Notification.objects.all().delete()
        Notification.objects.create(
            title="High Match Return Load Found!",
            message="Load 002 (Chennai → Ranchi, 18T Auto Parts) matched with 94% compatibility for truck JH01AB1234.",
            channel="in_app",
            category="match_alert"
        )
        Notification.objects.create(
            title="Empty KM Reduction Alert",
            message="Chaining Load 001 + Load 002 saves 1,620 empty return kilometers and adds ₹78,000 extra revenue.",
            channel="whatsapp",
            category="match_alert"
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded TruckFlow Step 26 demo data!"))
