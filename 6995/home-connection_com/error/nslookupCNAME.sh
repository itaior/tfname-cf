#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "home-connection.com" "grabaufkaviot2lek5sms3uql626bctg._domainkey.home-connection.com" "owk27gvjr2sacow6gayhchwdrqkjca5n._domainkey.home-connection.com" "uu2e5tfptxouvlrqzeet6ad57myykcga._domainkey.home-connection.com" "k1._domainkey.home-connection.com.home-connection.com" "www.home-connection.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done