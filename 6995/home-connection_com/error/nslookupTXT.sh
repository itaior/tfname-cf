#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "home-connection.com" "home-connection.com.home-connection.com" "_amazonses.home-connection.com" "_dmarc.home-connection.com" "20180628-nfh3hlt7._domainkey.home-connection.com" "spop1024._domainkey.home-connection.com" "email.home-connection.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[TXT] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorTXT.txt 
done