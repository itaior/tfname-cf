#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "homeperks.com" "homeperks.com.homeperks.com" "email.homeperks.com" "mail.homeperks.com" "pge.homeperks.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[MX] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorMX.txt 
done