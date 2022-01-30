#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "activationcenter.com" "_domainconnect.activationcenter.com" "e.activationcenter.com" "email.activationcenter.com" "ftp.activationcenter.com" "imap.activationcenter.com" "mobilemail.activationcenter.com" "pda.activationcenter.com" "pop.activationcenter.com" "smtp.activationcenter.com" "webmail.activationcenter.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done