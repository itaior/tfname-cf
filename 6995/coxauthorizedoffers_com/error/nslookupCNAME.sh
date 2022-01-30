#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "coxauthorizedoffers.com" "_domainconnect.coxauthorizedoffers.com" "b.coxauthorizedoffers.com" "cart.coxauthorizedoffers.com" "_3e3383106a1e2a6417d053f228535579.cart.coxauthorizedoffers.com" "email.coxauthorizedoffers.com" "ftp.coxauthorizedoffers.com" "imap.coxauthorizedoffers.com" "mail.coxauthorizedoffers.com" "mobilemail.coxauthorizedoffers.com" "pda.coxauthorizedoffers.com" "pop.coxauthorizedoffers.com" "smtp.coxauthorizedoffers.com" "webmail.coxauthorizedoffers.com" "www.coxauthorizedoffers.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done