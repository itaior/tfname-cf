#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "charterauthorizedoffers.com" "_domainconnect.charterauthorizedoffers.com" "e.charterauthorizedoffers.com" "email.charterauthorizedoffers.com" "ftp.charterauthorizedoffers.com" "imap.charterauthorizedoffers.com" "mail.charterauthorizedoffers.com" "mobilemail.charterauthorizedoffers.com" "pda.charterauthorizedoffers.com" "pop.charterauthorizedoffers.com" "smtp.charterauthorizedoffers.com" "webmail.charterauthorizedoffers.com" "www.charterauthorizedoffers.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done