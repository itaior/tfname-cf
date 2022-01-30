#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "homeperks.com" "_661fa9d34af4eb0832a86cf24bb1b8c1.homeperks.com" "k1._domainkey.homeperks.com" "api.homeperks.com" "cart.homeperks.com" "_f38accf6f94c74fa539116cdca6727b4.cart.homeperks.com" "cdn.homeperks.com" "email.email.homeperks.com" "grafana.homeperks.com" "email.mail.homeperks.com" "matomo.homeperks.com" "mautic-sp.homeperks.com" "mautic.homeperks.com" "old.homeperks.com" "k2._domainkey.pge.homeperks.com" "k3._domainkey.pge.homeperks.com" "phpmyadmin.homeperks.com" "webhook.homeperks.com" "www.homeperks.com" "_f178124828f541afbccce6d501bf201d.www.homeperks.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done