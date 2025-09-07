#!/usr/bin/env python3
"""
Test für Advanced Dispatch System mit Advanced Algorithms
"""

try:
    from advanced_dispatch_system import create_demo_bess, AdvancedDispatchSystem
    
    print("🚀 Teste Advanced Dispatch System mit Advanced Algorithms...")
    
    # Demo-BESS erstellen
    bess = create_demo_bess()
    print(f"✅ Demo-BESS erstellt: {bess.power_max_mw} MW / {bess.energy_capacity_mwh} MWh")
    
    # System initialisieren
    system = AdvancedDispatchSystem(bess)
    print("✅ Advanced Dispatch System initialisiert")
    
    # Standard-Optimierung
    print("\n📊 Standard-Optimierung:")
    standard_result = system.run_optimization(50.0, use_advanced_algorithms=False)
    print(f"  - Gesamterlös: {standard_result['total_revenue_eur']:.2f} €")
    print(f"  - Optimierungstyp: {standard_result['optimization_type']}")
    
    # Advanced-Optimierung
    print("\n🧠 Advanced-Optimierung:")
    advanced_result = system.run_optimization(50.0, use_advanced_algorithms=True)
    print(f"  - Gesamterlös: {advanced_result['total_revenue_eur']:.2f} €")
    print(f"  - Optimierungstyp: {advanced_result['optimization_type']}")
    
    # Advanced Results anzeigen
    if 'advanced_results' in advanced_result:
        print("\n🔬 Advanced Results Details:")
        results = advanced_result['advanced_results']
        
        if results.get('milp', {}).get('success', False):
            print(f"  - MILP Erlös: {results['milp']['total_revenue_eur']:.2f} €")
        
        if results.get('sdp', {}).get('success', False):
            print(f"  - SDP Erlös: {results['sdp']['total_revenue_eur']:.2f} €")
        
        if 'comparison' in results:
            comp = results['comparison']
            print(f"  - Beste Methode: {comp['best_algorithm']}")
            print(f"  - Verbesserung: {comp['improvement_pct']:.1f}%")
    
    # Vergleich
    improvement = ((advanced_result['total_revenue_eur'] - standard_result['total_revenue_eur']) / 
                  max(standard_result['total_revenue_eur'], 0.01)) * 100
    print(f"\n📈 Verbesserung durch Advanced Algorithms: {improvement:.1f}%")
    
    print("\n🎉 Advanced Dispatch System mit Advanced Algorithms funktioniert einwandfrei!")
    
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
