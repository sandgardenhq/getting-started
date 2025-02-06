#! /bin/bash

set -e

SCRIPT_DIR="$( dirname -- "${BASH_SOURCE[0]}" )"
source "${SCRIPT_DIR}/_load_env.sh"
load_env

SQL=$1

NET_OPT=""
if [[ "${DEMO_TYPE}" == "docker" ]]; then
  NET_OPT="--net=sandgarden_demo_network"
fi

# psql via docker -it with PGPASSWORD environment variable
docker run $NET_OPT -t --rm -e PGPASSWORD=$DB_PASS postgres psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -U $DB_USER --pset pager=off -c "$SQL"
