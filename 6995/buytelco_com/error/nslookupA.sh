#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "buytelco.com" "buytelco.com.buytelco.com" "dev.buytelco.com" "diagnostic.buytelco.com" "dtsserver.buytelco.com" "exchange.buytelco.com" "exchange1.buytelco.com" "highspeedoffers.buytelco.com" "im.buytelco.com" "mail.buytelco.com" "mia-corp-vir-02.buytelco.com" "mobile.buytelco.com" "netzero1.buytelco.com" "prodweb1.buytelco.com" "uat.buytelco.com" "vpn.buytelco.com" "vpn1.buytelco.com" "vpn2.buytelco.com" "www.buytelco.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[A] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorA.txt 
done
