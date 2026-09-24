import math

# Major Indian freight hubs with lat/lng
INDIAN_CITIES = {
    "Ranchi": {"state": "Jharkhand", "lat": 23.3441, "lng": 85.3096},
    "Jamshedpur": {"state": "Jharkhand", "lat": 22.8046, "lng": 86.2029},
    "Chennai": {"state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707},
    "Coimbatore": {"state": "Tamil Nadu", "lat": 11.0168, "lng": 76.9558},
    "Bhubaneswar": {"state": "Odisha", "lat": 20.2961, "lng": 85.8245},
    "Cuttack": {"state": "Odisha", "lat": 20.4625, "lng": 85.8830},
    "Kolkata": {"state": "West Bengal", "lat": 22.5726, "lng": 88.3639},
    "Visakhapatnam": {"state": "Andhra Pradesh", "lat": 17.6868, "lng": 83.2185},
    "Vijayawada": {"state": "Andhra Pradesh", "lat": 16.5062, "lng": 80.6480},
    "Hyderabad": {"state": "Telangana", "lat": 17.3850, "lng": 78.4867},
    "Bengaluru": {"state": "Karnataka", "lat": 12.9716, "lng": 77.5946},
    "Mumbai": {"state": "Maharashtra", "lat": 19.0760, "lng": 72.8777},
    "Delhi": {"state": "Delhi", "lat": 28.6139, "lng": 77.2090},
}

# Highway route distances in KM (Indian road network)
HIGHWAY_DISTANCES = {
    ("Ranchi", "Chennai"): 1620,
    ("Chennai", "Ranchi"): 1620,
    ("Chennai", "Bhubaneswar"): 1220,
    ("Bhubaneswar", "Chennai"): 1220,
    ("Bhubaneswar", "Ranchi"): 460,
    ("Ranchi", "Bhubaneswar"): 460,
    ("Kolkata", "Ranchi"): 410,
    ("Ranchi", "Kolkata"): 410,
    ("Chennai", "Hyderabad"): 630,
    ("Hyderabad", "Chennai"): 630,
    ("Chennai", "Bengaluru"): 350,
    ("Bengaluru", "Chennai"): 350,
}

# High-fidelity intermediate waypoints along the freight corridors for realistic map animation
CORRIDOR_WAYPOINTS = {
    ("Ranchi", "Chennai"): [
        [23.3441, 85.3096],  # Ranchi
        [22.8046, 86.2029],  # Jamshedpur
        [22.2850, 86.7350],  # Baharagora
        [21.5033, 86.9250],  # Balasore
        [20.8400, 86.2400],  # Bhadrak
        [20.4625, 85.8830],  # Cuttack
        [20.2961, 85.8245],  # Bhubaneswar
        [19.3150, 84.7940],  # Berhampur
        [18.2950, 83.8950],  # Srikakulam
        [17.6868, 83.2185],  # Visakhapatnam
        [16.9890, 82.2470],  # Kakinada junction
        [16.5062, 80.6480],  # Vijayawada
        [15.8281, 80.3542],  # Bapatla
        [15.5057, 80.0499],  # Ongole
        [14.4426, 79.9865],  # Nellore
        [13.6288, 80.0270],  # Gummidipoondi
        [13.0827, 80.2707],  # Chennai (Destination)
    ],
    ("Chennai", "Ranchi"): [
        [13.0827, 80.2707],  # Chennai
        [14.4426, 79.9865],  # Nellore
        [15.5057, 80.0499],  # Ongole
        [16.5062, 80.6480],  # Vijayawada
        [17.6868, 83.2185],  # Visakhapatnam
        [19.3150, 84.7940],  # Berhampur
        [20.2961, 85.8245],  # Bhubaneswar
        [20.4625, 85.8830],  # Cuttack
        [21.5033, 86.9250],  # Balasore
        [22.8046, 86.2029],  # Jamshedpur
        [23.3441, 85.3096],  # Ranchi
    ],
    ("Chennai", "Bhubaneswar"): [
        [13.0827, 80.2707],  # Chennai
        [14.4426, 79.9865],  # Nellore
        [16.5062, 80.6480],  # Vijayawada
        [17.6868, 83.2185],  # Visakhapatnam
        [19.3150, 84.7940],  # Berhampur
        [20.2961, 85.8245],  # Bhubaneswar
    ],
    ("Bhubaneswar", "Ranchi"): [
        [20.2961, 85.8245],  # Bhubaneswar
        [20.4625, 85.8830],  # Cuttack
        [21.0500, 85.2000],  # Keonjhar corridor
        [22.2500, 85.7500],  # Chaibasa
        [23.3441, 85.3096],  # Ranchi
    ]
}

def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance between two points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def get_route_distance(origin, destination):
    """Return highway driving distance in km or estimate via road factor."""
    pair = (origin, destination)
    if pair in HIGHWAY_DISTANCES:
        return HIGHWAY_DISTANCES[pair]
    
    # Fallback to geocoded distance with road winding factor of 1.28
    c1 = INDIAN_CITIES.get(origin)
    c2 = INDIAN_CITIES.get(destination)
    if c1 and c2:
        aerial = haversine_km(c1["lat"], c1["lng"], c2["lat"], c2["lng"])
        return int(round(aerial * 1.28))
    return 800  # generic fallback

def get_route_waypoints(origin, destination):
    """Return list of [lat, lng] waypoints for map animations."""
    pair = (origin, destination)
    if pair in CORRIDOR_WAYPOINTS:
        return CORRIDOR_WAYPOINTS[pair]
    
    # Generate linear interpolation between origin and destination
    c1 = INDIAN_CITIES.get(origin, {"lat": 23.3441, "lng": 85.3096})
    c2 = INDIAN_CITIES.get(destination, {"lat": 13.0827, "lng": 80.2707})
    
    pts = []
    steps = 10
    for i in range(steps + 1):
        ratio = i / steps
        lat = c1["lat"] + (c2["lat"] - c1["lat"]) * ratio
        lng = c1["lng"] + (c2["lng"] - c1["lng"]) * ratio
        pts.append([round(lat, 5), round(lng, 5)])
    return pts
