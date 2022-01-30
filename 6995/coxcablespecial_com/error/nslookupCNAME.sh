#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "coxcablespecial.com" "b.coxcablespecial.com" "cart.coxcablespecial.com" "_0dc32008081ccabd88bb5a22d9fe5108.cart.coxcablespecial.com" "order.coxcablespecial.com" "rewards.coxcablespecial.com" "www.coxcablespecial.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done