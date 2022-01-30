#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "dukeenergyconnections.com" "www.dukeenergyconnections.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done