#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "activationcenter.com" "activationcenter.com.activationcenter.com" "dal.activationcenter.com" "mia.activationcenter.com" "release.activationcenter.com" "test-dr-www.activationcenter.com" "www.activationcenter.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[A] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorA.txt 
done
