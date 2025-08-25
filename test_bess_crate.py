#!/usr/bin/env python3
"""
Test-Script für bess_crate Modul
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bess_crate_module():
    """Testet das bess_crate Modul"""
    
    try:
        from app.bess_crate import CRConfig, compute_power_bounds, derate_factors, test_config
        
        print("✅ bess_crate Modul erfolgreich importiert")
        
        # Test CRConfig
        config = CRConfig(
            E_nom_kWh=1000.0,
            C_chg_rate=0.5,
            C_dis_rate=1.0,
            derating_enable=True
        )
        print(f"✅ CRConfig erstellt: {config}")
        
        # Test compute_power_bounds
        bounds = compute_power_bounds(1000.0, 0.5, 1.0)
        print(f"✅ Power Bounds berechnet: {bounds}")
        
        # Test derate_factors
        factors = derate_factors(0.5, 25.0, config)
        print(f"✅ Derating Faktoren: {factors}")
        
        # Test test_config
        test_data = {
            'E_nom_kWh': 1000.0,
            'C_chg_rate': 0.5,
            'C_dis_rate': 1.0,
            'derating_enable': True,
            'soc_derate_charge': [[0.0, 0.2, 0.2], [0.2, 0.8, 1.0], [0.8, 1.0, 0.5]],
            'soc_derate_discharge': [[0.0, 0.2, 0.7], [0.2, 0.8, 1.0], [0.8, 1.0, 0.8]],
            'temp_derate_charge': [[-20, 0, 0.2], [0, 10, 0.6], [10, 35, 1.0], [35, 50, 0.7]],
            'temp_derate_discharge': [[-20, 0, 0.6], [0, 10, 0.9], [10, 35, 1.0], [35, 50, 0.9]]
        }
        
        result = test_config(test_data, 0.5, 25.0)
        print(f"✅ Test Config Ergebnis: {result}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Test-Fehler: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Teste bess_crate Modul...")
    success = test_bess_crate_module()
    
    if success:
        print("✅ bess_crate Modul funktioniert!")
    else:
        print("❌ bess_crate Modul hat Probleme!")
