#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "homeperks.io" "homeperks.io.homeperks.io" "email.homeperks.io" "pic._domainkey.email.homeperks.io" "mail.homeperks.io" "pic._domainkey.mail.homeperks.io" "matomo.homeperks.io" "mautic-sp.homeperks.io" "mautic.homeperks.io" "webhook.homeperks.io" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[TXT] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorTXT.txt 
done