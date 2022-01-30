#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "mediacomauthorizedoffers.com" "_domainconnect.mediacomauthorizedoffers.com" "b.mediacomauthorizedoffers.com" "cart.mediacomauthorizedoffers.com" "_380a1148a8fa933263a68af4be959b1c.cart.mediacomauthorizedoffers.com" "e.mediacomauthorizedoffers.com" "email.mediacomauthorizedoffers.com" "ftp.mediacomauthorizedoffers.com" "imap.mediacomauthorizedoffers.com" "mail.mediacomauthorizedoffers.com" "mobilemail.mediacomauthorizedoffers.com" "pda.mediacomauthorizedoffers.com" "pop.mediacomauthorizedoffers.com" "smtp.mediacomauthorizedoffers.com" "webmail.mediacomauthorizedoffers.com" "www.mediacomauthorizedoffers.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done