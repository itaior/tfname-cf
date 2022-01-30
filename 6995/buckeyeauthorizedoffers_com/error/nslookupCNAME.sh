#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "buckeyeauthorizedoffers.com" "_domainconnect.buckeyeauthorizedoffers.com" "b.buckeyeauthorizedoffers.com" "e.buckeyeauthorizedoffers.com" "email.buckeyeauthorizedoffers.com" "ftp.buckeyeauthorizedoffers.com" "imap.buckeyeauthorizedoffers.com" "mail.buckeyeauthorizedoffers.com" "mobilemail.buckeyeauthorizedoffers.com" "pda.buckeyeauthorizedoffers.com" "pop.buckeyeauthorizedoffers.com" "smtp.buckeyeauthorizedoffers.com" "webmail.buckeyeauthorizedoffers.com" "www.buckeyeauthorizedoffers.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done