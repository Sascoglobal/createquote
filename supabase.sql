-- Run once in Supabase: SQL Editor > New query > paste > Run.
-- Then put the project URL and anon key into CONFIG at the top of the script in index.html.

create table if not exists public.quotes (
  id                uuid primary key default gen_random_uuid(),
  quote_no          text unique not null,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz,
  created_by_email  text not null,
  created_by_name   text,
  mode              text,
  direction         text,
  load_type         text,
  cargo_nature      text,
  cargo_type        text,
  incoterm          text,
  client_company    text,
  client_contact    text,
  client_email      text,
  currency          text,
  subtotal          numeric,
  discount          numeric,
  vat               numeric,
  total             numeric,
  payload           jsonb
);

create index if not exists quotes_created_by_idx on public.quotes (created_by_email);
create index if not exists quotes_created_at_idx on public.quotes (created_at desc);

alter table public.quotes enable row level security;

-- The app sends the public anon key. These policies let it read, insert and update quotes,
-- but only rows owned by a @sascoglobal.com address can be written.
-- NOTE: with a typed-email gate this is convenience, not security. Anyone who finds the anon key
-- could read or write quotes. Move to Supabase Auth (email OTP) before storing sensitive client data.
drop policy if exists quotes_read on public.quotes;
drop policy if exists quotes_insert on public.quotes;
drop policy if exists quotes_update on public.quotes;
create policy quotes_read   on public.quotes for select to anon using (true);
create policy quotes_insert on public.quotes for insert to anon with check (created_by_email ilike '%@sascoglobal.com');
create policy quotes_update on public.quotes for update to anon using (true) with check (created_by_email ilike '%@sascoglobal.com');

-- Handy report: quotations per salesperson
create or replace view public.quotes_by_salesperson as
  select created_by_email,
         max(created_by_name) as name,
         count(*)             as quotes,
         count(*) filter (where date_trunc('month', created_at) = date_trunc('month', now())) as this_month,
         max(created_at)      as last_quote
  from public.quotes
  group by created_by_email
  order by quotes desc;
