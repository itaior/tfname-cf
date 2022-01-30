#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "mediacomspecial.com" "mediacomspecial.com.mediacomspecial.com" "secure.mediacomspecial.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[A] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorA.txt 
done
