#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "brighthouseofficialoffers.com" "_domainconnect.brighthouseofficialoffers.com" "e.brighthouseofficialoffers.com" "email.brighthouseofficialoffers.com" "ftp.brighthouseofficialoffers.com" "imap.brighthouseofficialoffers.com" "mail.brighthouseofficialoffers.com" "mobilemail.brighthouseofficialoffers.com" "pda.brighthouseofficialoffers.com" "pop.brighthouseofficialoffers.com" "smtp.brighthouseofficialoffers.com" "webmail.brighthouseofficialoffers.com" "www.brighthouseofficialoffers.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done