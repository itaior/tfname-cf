#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "digitalcommercenow.com" "_domainconnect.digitalcommercenow.com" "e.digitalcommercenow.com" "email.digitalcommercenow.com" "ftp.digitalcommercenow.com" "imap.digitalcommercenow.com" "mail.digitalcommercenow.com" "mobilemail.digitalcommercenow.com" "pda.digitalcommercenow.com" "pop.digitalcommercenow.com" "smtp.digitalcommercenow.com" "webmail.digitalcommercenow.com" "www.digitalcommercenow.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done