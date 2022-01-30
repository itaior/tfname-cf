#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "mobilebroadbandnow.com" "_domainconnect.mobilebroadbandnow.com" "e.mobilebroadbandnow.com" "email.mobilebroadbandnow.com" "ftp.mobilebroadbandnow.com" "imap.mobilebroadbandnow.com" "mail.mobilebroadbandnow.com" "mobilemail.mobilebroadbandnow.com" "pda.mobilebroadbandnow.com" "pop.mobilebroadbandnow.com" "smtp.mobilebroadbandnow.com" "webmail.mobilebroadbandnow.com" "www.mobilebroadbandnow.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done