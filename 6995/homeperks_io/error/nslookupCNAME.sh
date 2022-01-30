#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "homeperks.io" "*.homeperks.io" "_5b8b0f36de1cddba2ed828f94e71f6e8.homeperks.io" "api.homeperks.io" "cdn.homeperks.io" "email.email.homeperks.io" "email.mail.homeperks.io" "matomo.homeperks.io" "mautic-sp.homeperks.io" "mautic.homeperks.io" "webhook.homeperks.io" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done