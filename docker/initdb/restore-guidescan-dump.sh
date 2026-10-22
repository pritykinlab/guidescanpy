#!/bin/sh
# Restores a guidescan database dump (created with `pg_dump -Fc`) mounted at
# /guidescan.dump. The postgres image runs this (from /docker-entrypoint-initdb.d)
# only when the database volume is first created.

# Restoring a dump from an older Postgres version can produce harmless errors
# (e.g. about the plpgsql extension), so don't abort initialization on these.
pg_restore --no-owner --no-acl --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" /guidescan.dump \
    || echo "pg_restore reported errors (see above), continuing"

# Fails initialization if the restore didn't create the tables guidescan needs
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
    -c "SELECT organism, count(*) AS chromosomes FROM chromosomes GROUP BY organism ORDER BY organism;"
