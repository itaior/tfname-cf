#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "acceller.com" "acceller.com.acceller.com" "_dmarc.acceller.com" "google._domainkey.acceller.com" "vz.acceller.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[TXT] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorTXT.txt 
done