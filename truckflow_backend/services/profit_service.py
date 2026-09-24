def calculate_trip_profit(
    total_km,
    loaded_km,
    empty_km,
    total_freight,
    diesel_price_per_litre=92.50,
    kmpl=3.5,
    toll_per_km=4.20,
    driver_expense_daily=1200,
    days_duration=4,
    broker_commission_pct=3.0,
    loading_charges=2500,
    maintenance_per_km=2.0
):
    """
    Calculate full financial breakdown for a proposed trip.
    """
    # Fuel cost
    litres_needed = total_km / float(kmpl)
    fuel_cost = litres_needed * float(diesel_price_per_litre)
    
    # Toll expenses (FASTag calculation on National Highways)
    toll_cost = total_km * float(toll_per_km)
    
    # Driver allowance (Bata + halts)
    driver_cost = driver_expense_daily * days_duration
    
    # Broker commission
    commission_cost = total_freight * (broker_commission_pct / 100.0)
    
    # Vehicle maintenance buffer
    maintenance_cost = total_km * maintenance_per_km
    
    total_expenses = fuel_cost + toll_cost + driver_cost + commission_cost + loading_charges + maintenance_cost
    net_profit = total_freight - total_expenses
    profit_margin = (net_profit / total_freight * 100.0) if total_freight > 0 else 0.0
    profit_per_km = net_profit / total_km if total_km > 0 else 0.0
    revenue_per_km = total_freight / total_km if total_km > 0 else 0.0
    
    return {
        "gross_revenue": round(total_freight, 2),
        "total_expenses": round(total_expenses, 2),
        "net_profit": round(net_profit, 2),
        "profit_margin_pct": round(profit_margin, 1),
        "revenue_per_km": round(revenue_per_km, 2),
        "profit_per_km": round(profit_per_km, 2),
        "breakdown": {
            "fuel_cost": round(fuel_cost, 2),
            "toll_cost": round(toll_cost, 2),
            "driver_cost": round(driver_cost, 2),
            "commission_cost": round(commission_cost, 2),
            "loading_charges": round(loading_charges, 2),
            "maintenance_cost": round(maintenance_cost, 2),
        },
        "metrics": {
            "total_km": total_km,
            "loaded_km": loaded_km,
            "empty_km": empty_km,
            "empty_km_pct": round((empty_km / total_km * 100), 1) if total_km > 0 else 0.0
        }
    }

def compare_scenarios(outbound_freight=85000, outbound_km=1620, return_freight=78000, return_km=1620):
    """
    Side-by-side comparison:
    Scenario A: Without Return Load (Truck returns empty)
    Scenario B: With Return Load (Fully utilized round trip)
    """
    total_km = outbound_km + return_km
    
    # Scenario A: Empty Return
    scen_a = calculate_trip_profit(
        total_km=total_km,
        loaded_km=outbound_km,
        empty_km=return_km,
        total_freight=outbound_freight
    )
    
    # Scenario B: With Return Load
    scen_b = calculate_trip_profit(
        total_km=total_km,
        loaded_km=total_km,
        empty_km=0,
        total_freight=outbound_freight + return_freight
    )
    
    profit_diff = scen_b["net_profit"] - scen_a["net_profit"]
    
    return {
        "without_return_load": scen_a,
        "with_return_load": scen_b,
        "additional_profit_gained": round(profit_diff, 2),
        "empty_km_saved": return_km,
        "roi_increase_factor": round(scen_b["net_profit"] / max(1, scen_a["net_profit"]), 1) if scen_a["net_profit"] > 0 else "Infinite (Turned Loss to Profit)"
    }
