create table users (
  id uuid primary key default gen_random_uuid(),
  username text unique not null,
  password_hash text not null,
  created_at timestamptz default now()
);

create table sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  session_id text not null,
  label text,
  created_at timestamptz default now(),
  expires_at timestamptz default (now() + interval '7 days')
);

create table medical_history (
  session_id text primary key,
  data jsonb not null,
  created_at timestamptz default now()
);