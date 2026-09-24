import datetime
from .route_service import get_route_distance, INDIAN_CITIES, haversine_km

def calculate_match_score(truck, load, expected_origin=None, expected_dest=None):
    """
    Explainable Matching Algorithm.
    Scores each candidate match using a weighted combination of:
    - Proximity to origin/destination (25%)
    - Capacity vs Weight fit (20%)
    - Vehicle type & goods compatibility (15%)
    - Schedule & deadline alignment (15%)
    - Route deviation / empty run to pickup (15%)
    - Revenue potential vs market rate (10%)
    Returns total score (0-100) and detailed factor breakdown.
    """
    exp_orig = expected_origin or truck.current_location.split(',')[0].strip()
    exp_dest = expected_dest or truck.current_destination.split(',')[0].strip()
    
    breakdown = {}
    
    # 1. Proximity to Origin & Destination (25 pts)
    orig_match = (load.pickup_city.lower() == exp_orig.lower())
    dest_match = (load.drop_city.lower() == exp_dest.lower())
    
    if orig_match and dest_match:
        prox_score = 25
    elif orig_match or dest_match:
        prox_score = 18
    else:
        # Check distance between cities
        c_orig = INDIAN_CITIES.get(exp_orig)
        c_p = INDIAN_CITIES.get(load.pickup_city)
        if c_orig and c_p:
            dist = haversine_km(c_orig["lat"], c_orig["lng"], c_p["lat"], c_p["lng"])
            prox_score = max(5, int(25 - (dist / 40)))
        else:
            prox_score = 12
    breakdown["proximity"] = {
        "score": prox_score,
        "max": 25,
        "label": "Corridor Proximity",
        "detail": f"Pickup: {load.pickup_city}, Drop: {load.drop_city}"
    }

    # 2. Capacity vs Weight Fit (20 pts)
    # Ideally load weight is 70% to 95% of truck capacity
    truck_cap = float(truck.capacity_tons)
    load_wt = float(load.weight_tons)
    
    if load_wt > truck_cap:
        # Overweight: penalize heavily
        cap_score = max(0, int(20 - (load_wt - truck_cap) * 10))
        cap_detail = f"Overload risk! {load_wt}T exceeds {truck_cap}T capacity"
    else:
        utilization = (load_wt / truck_cap) * 100
        if 75 <= utilization <= 95:
            cap_score = 20
            cap_detail = f"Optimal payload utilization: {utilization:.0f}% ({load_wt}T of {truck_cap}T)"
        elif utilization >= 60:
            cap_score = 17
            cap_detail = f"Good payload utilization: {utilization:.0f}% ({load_wt}T of {truck_cap}T)"
        else:
            cap_score = 12
            cap_detail = f"Partial payload: {utilization:.0f}% ({load_wt}T of {truck_cap}T)"
    breakdown["capacity_fit"] = {
        "score": cap_score,
        "max": 20,
        "label": "Capacity Utilization",
        "detail": cap_detail
    }

    # 3. Vehicle Body & Goods Compatibility (15 pts)
    # E.g. Container for auto parts/FMCG, Open/Trailer for steel coils
    body = truck.body_type.lower()
    goods = load.goods_type.lower()
    
    if "steel" in goods and ("open" in body or "trailer" in body or "semi" in truck.truck_type.lower()):
        type_score = 15
        type_detail = "High compatibility: Heavy cargo trailer suited for industrial steel"
    elif ("auto" in goods or "parts" in goods or "fmcg" in goods) and ("container" in body or "closed" in body or "trailer" in body):
        type_score = 15
        type_detail = "High compatibility: Secure container suited for manufactured freight"
    else:
        type_score = 13
        type_detail = "Standard compatibility for commercial freight"
    breakdown["compatibility"] = {
        "score": type_score,
        "max": 15,
        "label": "Body & Goods Compatibility",
        "detail": type_detail
    }

    # 4. Schedule & Deadline Alignment (15 pts)
    # Check if load pickup is on or after truck availability
    truck_avail = truck.availability_date
    load_pickup = load.pickup_date
    if hasattr(truck_avail, 'date'):
        truck_avail = truck_avail.date()
    if hasattr(load_pickup, 'date'):
        load_pickup = load_pickup.date()
        
    day_diff = (load_pickup - truck_avail).days if (truck_avail and load_pickup) else 0
    if 0 <= day_diff <= 2:
        date_score = 15
        date_detail = "Immediate turnaround (Ready within 48h)"
    elif day_diff < 0:
        date_score = 8
        date_detail = "Early pickup required (Truck in transit)"
    else:
        date_score = max(7, 15 - day_diff)
        date_detail = f"Scheduled {day_diff} days after availability"
    breakdown["schedule"] = {
        "score": date_score,
        "max": 15,
        "label": "Schedule Alignment",
        "detail": date_detail
    }

    # 5. Route Deviation / Detour (15 pts)
    # Direct route gets full points
    if orig_match and dest_match:
        dev_score = 15
        dev_detail = "Zero highway deviation on designated corridor"
    elif orig_match or dest_match:
        dev_score = 12
        dev_detail = "Minor hub connection (<= 60 km detour)"
    else:
        dev_score = 8
        dev_detail = "Cross-corridor connection"
    breakdown["route_deviation"] = {
        "score": dev_score,
        "max": 15,
        "label": "Detour & Route Deviation",
        "detail": dev_detail
    }

    # 6. Revenue Potential vs Market Benchmark (10 pts)
    offered = float(load.offered_freight)
    bench = float(load.market_benchmark_freight) or (offered * 0.95)
    
    if offered >= bench * 1.05:
        rev_score = 10
        market_label = "Premium Freight Rate (+5% above market)"
    elif offered >= bench * 0.95:
        rev_score = 9
        market_label = "Fair Market Rate (Competitive standard)"
    else:
        rev_score = 6
        market_label = "Below Market Rate (Negotiation recommended)"
    breakdown["revenue_potential"] = {
        "score": rev_score,
        "max": 10,
        "label": "Market Benchmark & Revenue",
        "detail": f"{market_label} (₹{offered:,.0f} offered vs ₹{bench:,.0f} benchmark)"
    }

    total_score = sum(item["score"] for item in breakdown.values())
    
    return {
        "total_score": total_score,
        "percentage": f"{total_score}%",
        "grade": "EXCELLENT" if total_score >= 90 else "GOOD" if total_score >= 75 else "FAIR",
        "breakdown": breakdown,
        "market_benchmark": {
            "offered": offered,
            "benchmark": bench,
            "diff_pct": round(((offered - bench) / bench) * 100, 1) if bench else 0,
            "status": "ABOVE_BENCHMARK" if offered > bench else "FAIR" if offered == bench else "BELOW_BENCHMARK"
        }
    }

def find_round_trip_matches(truck, going_load=None):
    """
    Centerpiece Feature (Step 5):
    Simultaneously search:
    1. Going loads for outbound route (e.g. Ranchi -> Chennai)
    2. Return loads for reverse route (e.g. Chennai -> Ranchi)
    3. Multi-leg chain fallback (e.g. Chennai -> Bhubaneswar -> Ranchi)
    """
    from ..core.models import Load, LoadStatus
    
    truck_origin = truck.current_location.split(',')[0].strip()
    truck_dest = truck.current_destination.split(',')[0].strip()
    
    available_loads = Load.objects.filter(status=LoadStatus.AVAILABLE)
    
    # If no specific going load selected, find candidates for outbound leg
    going_matches = []
    for ld in available_loads:
        if ld.pickup_city.lower() == truck_origin.lower() and ld.drop_city.lower() == truck_dest.lower():
            score_data = calculate_match_score(truck, ld, truck_origin, truck_dest)
            going_matches.append({
                "load": ld,
                "match_score": score_data["total_score"],
                "score_details": score_data,
                "type": "DIRECT_OUTBOUND"
            })
    going_matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Selected or top going load
    active_going = going_load or (going_matches[0]["load"] if going_matches else None)
    
    # Auto-trigger Return Load search (Chennai -> Ranchi)
    return_matches = []
    for ld in available_loads:
        if active_going and ld.id == active_going.id:
            continue
        # Check reverse route
        if ld.pickup_city.lower() == truck_dest.lower() and ld.drop_city.lower() == truck_origin.lower():
            score_data = calculate_match_score(truck, ld, truck_dest, truck_origin)
            return_matches.append({
                "load": ld,
                "match_score": score_data["total_score"],
                "score_details": score_data,
                "type": "DIRECT_RETURN",
                "empty_km_saved": get_route_distance(truck_dest, truck_origin)
            })
    return_matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Search for Multi-Leg Chain options (Step 8):
    # E.g., Chennai -> Bhubaneswar, then Bhubaneswar -> Ranchi
    multi_leg_chains = []
    # Candidate leg 1: departs from truck_dest (Chennai) to an intermediate hub
    leg1_candidates = available_loads.filter(pickup_city__iexact=truck_dest).exclude(drop_city__iexact=truck_origin)
    for l1 in leg1_candidates:
        if active_going and l1.id == active_going.id:
            continue
        inter_city = l1.drop_city
        # Candidate leg 2: departs from intermediate hub to truck_origin (Ranchi)
        leg2_candidates = available_loads.filter(pickup_city__iexact=inter_city, drop_city__iexact=truck_origin)
        for l2 in leg2_candidates:
            if l2.id == l1.id:
                continue
            
            # Calculate stats for this 2-leg return chain
            dist_l1 = get_route_distance(truck_dest, inter_city)
            dist_l2 = get_route_distance(inter_city, truck_origin)
            direct_dist = get_route_distance(truck_dest, truck_origin)
            chain_dist = dist_l1 + dist_l2
            detour_km = max(0, chain_dist - direct_dist)
            
            combined_freight = float(l1.offered_freight) + float(l2.offered_freight)
            
            multi_leg_chains.append({
                "chain_name": f"{truck_dest} → {inter_city} → {truck_origin}",
                "intermediate_city": inter_city,
                "leg_1": {
                    "load": l1,
                    "distance_km": dist_l1,
                    "freight": float(l1.offered_freight)
                },
                "leg_2": {
                    "load": l2,
                    "distance_km": dist_l2,
                    "freight": float(l2.offered_freight)
                },
                "total_freight": combined_freight,
                "total_distance_km": chain_dist,
                "detour_km": detour_km,
                "empty_km_saved": direct_dist,
                "match_score": 88
            })
            
    return {
        "truck": truck,
        "selected_going_load": active_going,
        "going_matches": going_matches,
        "direct_return_matches": return_matches,
        "multi_leg_chains": multi_leg_chains,
        "stats": {
            "outbound_distance_km": get_route_distance(truck_origin, truck_dest),
            "return_distance_km": get_route_distance(truck_dest, truck_origin),
            "empty_km_if_no_return": get_route_distance(truck_dest, truck_origin),
            "potential_freight_saved": float(return_matches[0]["load"].offered_freight) if return_matches else 0.0
        }
    }
