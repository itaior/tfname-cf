#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "updater.team" "updater.team.updater.team" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[TXT] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorTXT.txt 
done