#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "bridgevine.io" "_amazonses.bridgevine.io" "email.bridgevine.io" "k1._domainkey.email.bridgevine.io" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[TXT] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorTXT.txt 
done