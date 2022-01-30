#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "bridgevine.io" "admin.bridgevine.io" "crm-old.bridgevine.io" "dev.bridgevine.io" "qa.bridgevine.io" "staging.bridgevine.io" "test.bridgevine.io" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[NS] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorNS.txt 
done