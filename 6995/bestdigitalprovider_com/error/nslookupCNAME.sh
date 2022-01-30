#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "bestdigitalprovider.com" "_domainconnect.bestdigitalprovider.com" "e.bestdigitalprovider.com" "email.bestdigitalprovider.com" "ftp.bestdigitalprovider.com" "imap.bestdigitalprovider.com" "mail.bestdigitalprovider.com" "mobilemail.bestdigitalprovider.com" "pda.bestdigitalprovider.com" "pop.bestdigitalprovider.com" "smtp.bestdigitalprovider.com" "webmail.bestdigitalprovider.com" "www.bestdigitalprovider.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done