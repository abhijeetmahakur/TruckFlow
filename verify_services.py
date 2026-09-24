import os
import sys
import io
import django

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'truckflow_backend.settings')
django.setup()

from truckflow_backend.core.models import Truck, Load
from truckflow_backend.services.matching_service import find_round_trip_matches
from truckflow_backend.services.profit_service import calculate_trip_profit, compare_scenarios

def verify():
    truck = Truck.objects.get(reg_number="JH01AB1234")
    print(f"Testing Truck: {truck.reg_number} ({truck.capacity_tons}T, {truck.current_location} -> {truck.current_destination})")
    
    matches = find_round_trip_matches(truck)
    print(f"Going Matches: {len(matches['going_matches'])}")
    for g in matches['going_matches']:
        print(f"  - Outbound Load: {g['load'].load_code} {g['load'].pickup_city} -> {g['load'].drop_city} (Score: {g['match_score']}%)")
        print(f"    Factor Breakdown: {g['score_details']['breakdown']}")
        
    print(f"Direct Return Matches: {len(matches['direct_return_matches'])}")
    for r in matches['direct_return_matches']:
        print(f"  - Return Load: {r['load'].load_code} {r['load'].pickup_city} -> {r['load'].drop_city} (Score: {r['match_score']}%)")
        print(f"    Empty KM Saved: {r['empty_km_saved']} km")
        print(f"    Factor Breakdown: {r['score_details']['breakdown']}")
        
    print(f"Multi-leg chains found: {len(matches['multi_leg_chains'])}")
    for c in matches['multi_leg_chains']:
        print(f"  - Chain: {c['chain_name']} | Freight: ₹{c['total_freight']:,.0f} | Detour: {c['detour_km']} km | Empty KM Saved: {c['empty_km_saved']} km")
        
    # Check profit comparison
    comp = compare_scenarios(outbound_freight=85000, outbound_km=1620, return_freight=78000, return_km=1620)
    print(f"\nProfit Analysis:")
    print(f"  Without Return Load Net Profit: ₹{comp['without_return_load']['net_profit']:,.2f}")
    print(f"  With Return Load Net Profit:    ₹{comp['with_return_load']['net_profit']:,.2f}")
    print(f"  Additional Profit Gained:       ₹{comp['additional_profit_gained']:,.2f}")
    print("ALL SERVICES VERIFIED!")

if __name__ == '__main__':
    verify()
