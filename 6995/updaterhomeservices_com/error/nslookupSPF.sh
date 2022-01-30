#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "updaterhomeservices.com" "updaterhomeservices.com.updaterhomeservices.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[TXT] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorTXT.txt 
done