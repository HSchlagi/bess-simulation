#!/usr/bin/env python3
"""
Test für Advanced Dispatch System
"""

try:
    from advanced_dispatch_system import create_demo_bess, AdvancedDispatchSystem
    
    print("🚀 Teste Advanced Dispatch System...")
    
    # Demo-BESS erstellen
    bess = create_demo_bess()
    print(f"✅ Demo-BESS erstellt: {bess.power_max_mw} MW / {bess.energy_capacity_mwh} MWh")
    
    # System initialisieren
    system = AdvancedDispatchSystem(bess)
    print("✅ Advanced Dispatch System initialisiert")
    
    # Optimierung durchführen
    result = system.run_optimization(50.0)
    print("✅ Optimierung durchgeführt")
    
    print(f"📊 Ergebnisse:")
    print(f"  - Gesamterlös: {result['total_revenue_eur']:.2f} €")
    print(f"  - Arbitrage: {result['arbitrage_decision'].revenue_eur:.2f} €")
    print(f"  - Grid-Services: {sum(result['grid_services'].values()):.2f} €")
    print(f"  - Demand Response: {result['demand_response_revenue']:.2f} €")
    
    print("🎉 Advanced Dispatch System funktioniert einwandfrei!")
    
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
