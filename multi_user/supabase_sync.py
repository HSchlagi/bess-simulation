
import os
from supabase import create_client, Client

# 🔧 Supabase Konfiguration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ⛔ Benutzer-Login erforderlich
USER_EMAIL = input("E-Mail: ")
USER_PASSWORD = input("Passwort: ")

# 🔐 Anmeldung
try:
    auth_response = supabase.auth.sign_in_with_password({"email": USER_EMAIL, "password": USER_PASSWORD})
    user = auth_response.user
    print(f"✅ Eingeloggt als: {user.email}")
except Exception as e:
    print("❌ Login fehlgeschlagen:", e)
    exit(1)

# 📦 Projekte des Nutzers abrufen
projects = supabase.table("projects").select("*").eq("user_id", user.id).execute()
print(f"📁 {len(projects.data)} Projekte gefunden:")

for project in projects.data:
    print(f"- {project['name']} ({project['id']})")

    # 🔄 Simulationsergebnisse für dieses Projekt abrufen
    simulations = supabase.table("simulation_results").select("*").eq("project_id", project["id"]).execute()
    print(f"  🔋 {len(simulations.data)} Simulationen:")
    for sim in simulations.data:
        print(f"    {sim['timestamp']}: {sim['capacity_kwh']} kWh | SoC: {sim['state_of_charge']}%")
