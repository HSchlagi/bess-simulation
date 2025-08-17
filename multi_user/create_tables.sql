
-- Projekte-Tabelle
create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  name text not null,
  created_at timestamp default now()
);

-- Simulationsergebnisse-Tabelle
create table if not exists simulation_results (
  id serial primary key,
  project_id uuid references projects(id) on delete cascade,
  timestamp timestamp default now(),
  capacity_kwh real,
  state_of_charge real
);
