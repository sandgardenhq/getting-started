#! /bin/bash

set -e

export DB_HOST="postgres"
export DB_PORT="5432"
export DB_NAME="tickets"
export DB_USER="tickets"
export DB_PASS="devpassword"

SQL=$1

NET_OPT="--net=sandgarden_demo_network"

# psql via docker -it with PGPASSWORD environment variable
docker run $NET_OPT -t --rm -e PGPASSWORD=$DB_PASS postgres psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -U $DB_USER --pset pager=off -c "$SQL"
