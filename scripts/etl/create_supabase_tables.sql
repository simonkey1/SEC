-- Tabla Key-Value para almacenar JSONs pre-cocinados para el Frontend
-- Esto permite que la web sea ultra-rapida (solo fetch by ID)

create table if not exists dashboard_stats (
  id text primary key, -- ej: 'market_map', 'time_series'
  data jsonb not null, -- El payload completo
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table dashboard_stats enable row level security;

-- Permitir lectura publica
create policy "Public Read Access" on dashboard_stats
  for select using (true);

-- FIX: Permitir escritura también (para el script de carga inicial)
-- En producción idealmente se usa Service Role, pero para desbloquear ahora:
create policy "Public Write Access" on dashboard_stats
  for insert with check (true);

create policy "Public Update Access" on dashboard_stats
  for update using (true);
