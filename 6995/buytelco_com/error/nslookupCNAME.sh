#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "buytelco.com" "_domainconnect.buytelco.com" "e.buytelco.com" "email.buytelco.com" "imap.buytelco.com" "mobilemail.buytelco.com" "ms34217317.buytelco.com" "pda.buytelco.com" "pop.buytelco.com" "smtp.buytelco.com" "webmail.buytelco.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done