#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "frontierauthorizedoffers.com" "_domainconnect.frontierauthorizedoffers.com" "b.frontierauthorizedoffers.com" "cart.frontierauthorizedoffers.com" "_b9d968ec4b7b68b28b09a792e8d5148c.cart.frontierauthorizedoffers.com" "e.frontierauthorizedoffers.com" "email.frontierauthorizedoffers.com" "ftp.frontierauthorizedoffers.com" "imap.frontierauthorizedoffers.com" "mail.frontierauthorizedoffers.com" "mobilemail.frontierauthorizedoffers.com" "pda.frontierauthorizedoffers.com" "pop.frontierauthorizedoffers.com" "smtp.frontierauthorizedoffers.com" "webmail.frontierauthorizedoffers.com" "www.frontierauthorizedoffers.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done