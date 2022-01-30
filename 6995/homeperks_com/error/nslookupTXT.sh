#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "homeperks.com" "homeperks.com.homeperks.com" "_dmarc.homeperks.com" "20180625-64ozzx41._domainkey.homeperks.com" "spop1024._domainkey.homeperks.com" "email.homeperks.com" "mx._domainkey.email.homeperks.com" "grafana.homeperks.com" "mail.homeperks.com" "smtp._domainkey.mail.homeperks.com" "matomo.homeperks.com" "mautic-sp.homeperks.com" "mautic.homeperks.com" "pge.homeperks.com" "www.pge.homeperks.com" "_cf-custom-hostname.www.pge.homeperks.com" "phpmyadmin.homeperks.com" "webhook.homeperks.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[TXT] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorTXT.txt 
done