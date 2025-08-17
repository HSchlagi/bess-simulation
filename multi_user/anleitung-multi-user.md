
# 🧠 Anleitung: BESS Simulation als Multi-User-System mit Supabase & Cursor AI

Diese Anleitung hilft dir, dein BESS-Simulationsprogramm in eine **multi-user-fähige Webanwendung** zu transformieren. Ziel ist es, dass **jeder Benutzer mehrere Projekte** verwalten und Simulationen ausführen kann, ohne Zugriff auf fremde Daten.

---

## 🔐 1. Benutzerverwaltung mit Supabase

- Verwende Supabase `auth.users` Tabelle (automatisch vorhanden)
- Login und Registrierung erfolgen über `supabase.auth.sign_up()` und `sign_in_with_password()`
- Jeder Benutzer hat eine eindeutige `id` (UUID), z. B. `auth.uid()`

---

## 🗂 2. Tabelle `projects` für Benutzer-Projekte

```sql
create table projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  name text not null,
  created_at timestamp default now()
);
```

- Jeder Benutzer kann mehrere Projekte haben (1:n)
- `user_id` referenziert `auth.users(id)`

---

## 📊 3. Tabelle `simulation_results` pro Projekt

```sql
create table simulation_results (
  id serial primary key,
  project_id uuid references projects(id) on delete cascade,
  timestamp timestamp default now(),
  capacity_kwh real,
  state_of_charge real
);
```

- Ergebnisse werden immer einem Projekt zugeordnet
- Kein direkter Bezug zu `user_id`, sondern über `projects.project_id`

---

## 🔒 4. Row-Level Security (RLS)

### a) Aktiviere RLS

```sql
alter table projects enable row level security;
alter table simulation_results enable row level security;
```

### b) Policies für `projects`

```sql
create policy "User can access their own projects"
on projects for all
using (auth.uid() = user_id);
```

### c) Policies für `simulation_results`

```sql
create policy "User can access simulation data through projects"
on simulation_results for all
using (
  auth.uid() = (
    select user_id from projects where projects.id = simulation_results.project_id
  )
);
```

---

## 🖥️ 5. Frontend-Logik mit Cursor AI

### Projektübersicht
- Nach Login: Lade alle Projekte des Benutzers via:
```js
supabase.from("projects").select("*").eq("user_id", user.id)
```

### Projekt anlegen
- POST `/api/projects` → Insert `name`, `user_id = auth.uid()`

### Simulation starten
- POST `/api/simulate` mit Daten + `project_id`

### Simulationsergebnisse laden
- GET `/api/simulations?project_id=...`

---

## 🛡 Sicherheitshinweis

- Verwende **nur den `anon` API Key** im Frontend
- Schütze den `service_role` Key strikt im Backend
- Aktiviere RLS und überprüfe, dass Policies für `SELECT`, `INSERT`, `UPDATE`, `DELETE` korrekt gesetzt sind

---

## 📁 Empfohlene Struktur

```
bess_webapp/
├── app.py
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── project_view.html
├── .env
├── requirements.txt
└── database/
    ├── create_tables.sql
    └── create_policies.sql
```

---

## ✅ Ergebnis

- Vollständig mehrbenutzerfähiges BESS-Portal
- Pro Benutzer beliebig viele Projekte & Simulationen
- Supabase verwaltet Authentifizierung und Datensicherheit

---

> Erstellt für Cursor AI – zur direkten Analyse, Generierung und Integration in dein bestehendes Flask- oder React-Projekt.
