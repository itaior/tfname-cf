#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "findyourinternet.com" "cart.findyourinternet.com" "_8d3e8cbc2afa97ef67c2f441059a2800.cart.findyourinternet.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done