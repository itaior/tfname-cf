#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "acceller.com" "_domainconnect.acceller.com" "affiliatepartners.acceller.com" "autodiscover.acceller.com" "cts2-dev.acceller.com" "cts2-qaf.acceller.com" "digitalinformer.acceller.com" "icsdigitalinformer.acceller.com" "lyncdiscover.acceller.com" "ms98010697.acceller.com" "msoid.acceller.com" "start.acceller.com" "watercooler.acceller.com" "wiki.acceller.com" "www.acceller.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done