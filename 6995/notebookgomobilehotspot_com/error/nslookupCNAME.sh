#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "notebookgomobilehotspot.com" "_domainconnect.notebookgomobilehotspot.com" "e.notebookgomobilehotspot.com" "email.notebookgomobilehotspot.com" "ftp.notebookgomobilehotspot.com" "imap.notebookgomobilehotspot.com" "mail.notebookgomobilehotspot.com" "mobilemail.notebookgomobilehotspot.com" "pda.notebookgomobilehotspot.com" "pop.notebookgomobilehotspot.com" "smtp.notebookgomobilehotspot.com" "webmail.notebookgomobilehotspot.com" "www.notebookgomobilehotspot.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done