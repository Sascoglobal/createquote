-- Run once in Supabase: SQL Editor > New query > paste > Run.
-- Company-wide currency rates. Everyone can READ; only someone who knows the admin PIN can WRITE (through save_fx).
create extension if not exists pgcrypto with schema extensions;

create table if not exists public.fx_settings (
  id          int primary key check (id = 1),
  rates       jsonb not null default '{}'::jsonb,
  fee         numeric not null default 0,
  updated_at  timestamptz,
  updated_by  text
);
create table if not exists public.app_admin (
  id        int primary key check (id = 1),
  pin_hash  text not null
);
alter table public.fx_settings enable row level security;
alter table public.app_admin  enable row level security;

drop policy if exists fx_read on public.fx_settings;
create policy fx_read on public.fx_settings for select to anon using (true);
-- no insert/update/delete policies on fx_settings, and no policies at all on app_admin: the browser cannot write rates or read the PIN directly.

-- Admin PIN (stored hashed). To change it later, run:  update public.app_admin set pin_hash = extensions.crypt('NEW PIN', extensions.gen_salt('bf')) where id = 1;
insert into public.app_admin (id, pin_hash) values (1, extensions.crypt('2311', extensions.gen_salt('bf')))
on conflict (id) do nothing;

create or replace function public.save_fx(p_pin text, p_rates jsonb, p_fee numeric, p_by text)
returns void language plpgsql security definer set search_path = public, extensions as $$
begin
  if not exists (select 1 from public.app_admin where pin_hash = crypt(p_pin, pin_hash)) then
    raise exception 'Wrong admin PIN';
  end if;
  insert into public.fx_settings (id, rates, fee, updated_at, updated_by)
  values (1, p_rates, coalesce(p_fee,0), now(), p_by)
  on conflict (id) do update set rates = excluded.rates, fee = excluded.fee, updated_at = now(), updated_by = excluded.updated_by;
end;
$$;
revoke all on function public.save_fx(text, jsonb, numeric, text) from public;
grant execute on function public.save_fx(text, jsonb, numeric, text) to anon;
