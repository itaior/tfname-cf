#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "coxofficialoffers.com" "_domainconnect.coxofficialoffers.com" "e.coxofficialoffers.com" "email.coxofficialoffers.com" "ftp.coxofficialoffers.com" "imap.coxofficialoffers.com" "mail.coxofficialoffers.com" "mobilemail.coxofficialoffers.com" "pda.coxofficialoffers.com" "pop.coxofficialoffers.com" "smtp.coxofficialoffers.com" "webmail.coxofficialoffers.com" "www.coxofficialoffers.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done