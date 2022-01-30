#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "tdsauthorizedoffers.com" "_domainconnect.tdsauthorizedoffers.com" "b.tdsauthorizedoffers.com" "calendar.tdsauthorizedoffers.com" "cart.tdsauthorizedoffers.com" "_3f99da0c3f89927999f1c6f26a08a2a6.cart.tdsauthorizedoffers.com" "email.tdsauthorizedoffers.com" "fax.tdsauthorizedoffers.com" "files.tdsauthorizedoffers.com" "ftp.tdsauthorizedoffers.com" "imap.tdsauthorizedoffers.com" "mail.tdsauthorizedoffers.com" "mobilemail.tdsauthorizedoffers.com" "pop.tdsauthorizedoffers.com" "smtp.tdsauthorizedoffers.com" "www.tdsauthorizedoffers.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done