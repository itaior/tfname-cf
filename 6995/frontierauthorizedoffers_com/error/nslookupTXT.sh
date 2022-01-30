#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "frontierauthorizedoffers.com" "frontierauthorizedoffers.com.frontierauthorizedoffers.com" "_cf-custom-hostname.frontierauthorizedoffers.com" "_dmarc.frontierauthorizedoffers.com" "spop1024._domainkey.frontierauthorizedoffers.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[TXT] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorTXT.txt 
done