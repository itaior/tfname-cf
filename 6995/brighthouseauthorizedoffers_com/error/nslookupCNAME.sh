#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "brighthouseauthorizedoffers.com" "_domainconnect.brighthouseauthorizedoffers.com" "b.brighthouseauthorizedoffers.com" "e.brighthouseauthorizedoffers.com" "email.brighthouseauthorizedoffers.com" "ftp.brighthouseauthorizedoffers.com" "imap.brighthouseauthorizedoffers.com" "mail.brighthouseauthorizedoffers.com" "mobilemail.brighthouseauthorizedoffers.com" "pda.brighthouseauthorizedoffers.com" "pop.brighthouseauthorizedoffers.com" "smtp.brighthouseauthorizedoffers.com" "webmail.brighthouseauthorizedoffers.com" "www.brighthouseauthorizedoffers.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done