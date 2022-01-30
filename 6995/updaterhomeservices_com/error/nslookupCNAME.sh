#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "updaterhomeservices.com" "updaterhomeservices.com.updaterhomeservices.com" "_97572c5913635ab2eceda2371a83aa58.updaterhomeservices.com" "cdn.updaterhomeservices.com" "_97572c5913635ab2eceda2371a83aa58.updaterhomeservices.com.updaterhomeservices.com" "www.updaterhomeservices.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done