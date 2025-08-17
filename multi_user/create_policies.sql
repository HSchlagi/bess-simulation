
-- RLS aktivieren
alter table projects enable row level security;
alter table simulation_results enable row level security;

-- Policy: Zugriff nur auf eigene Projekte
create policy "User can access their own projects"
on projects for all
using (auth.uid() = user_id);

-- Policy: Zugriff auf Simulationen nur über eigene Projekte
create policy "User can access simulation data through projects"
on simulation_results for all
using (
  auth.uid() = (
    select user_id from projects where projects.id = simulation_results.project_id
  )
);
