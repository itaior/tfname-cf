#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "wowwayspecial.com" "cart.wowwayspecial.com" "_075e841c2712844f930feaa9818a4508.cart.wowwayspecial.com" "www.wowwayspecial.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done