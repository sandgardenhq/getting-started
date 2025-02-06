#!/bin/bash

# This should be run when you are done with the example
# It will destroy the resources created by the setup script
# And return you to a totally empty state

# TODO: Reduce this back to all in one namespace
yes | sand steps delete --name="tickets_%"
yes | sand steps delete --name="escalate_checker%"
yes | sand steps delete --name="scan_tickets%"
yes | sand steps delete --name="save_results%"
yes | sand workflows delete --name="backfill%"
yes | sand workflows delete --name="composite%"

yes | sand connectors delete --name="tickets-%"
