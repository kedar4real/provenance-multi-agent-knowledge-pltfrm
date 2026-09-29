#!/bin/bash
# Runs once, on first start of an empty data volume. Creates the least-privilege login roles
# and a separate test database. Tables, grants and RLS policies come from db/migrations.
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
  -- Serves API requests. Never owns tables, so row-level security always applies to it.
  CREATE ROLE provenance_app LOGIN PASSWORD '${APP_DB_PASSWORD}';
  -- Runs model-generated SQL: read-only, short timeout, financial tables only.
  CREATE ROLE provenance_sql_ro LOGIN PASSWORD '${SQL_RO_DB_PASSWORD}';
  ALTER ROLE provenance_sql_ro SET default_transaction_read_only = on;
  ALTER ROLE provenance_sql_ro SET statement_timeout = '3s';
  CREATE DATABASE provenance_test OWNER provenance_owner;
SQL
