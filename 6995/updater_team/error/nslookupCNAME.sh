#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "updater.team" "_855a402d3d417f67b5ce54a12f224215.updater.team" "enterpriseenrollment.updater.team" "enterpriseregistration.updater.team" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done