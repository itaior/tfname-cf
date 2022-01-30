#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "bridgevine.io" "43zq2q5j4zfjcnfwidxnt6ifcgfbqolh._domainkey.bridgevine.io" "gm2bita4maax2w3plmy7t3zxiikedfqp._domainkey.bridgevine.io" "lg3y5tkyjbn7v4mifuikbr6ae6zqkxtz._domainkey.bridgevine.io" "_fcb4391bf5e9f52f1b0d9ffcb74d014b.bridgevine.io" "api.bridgevine.io" "code-backup.bridgevine.io" "crm.bridgevine.io" "email.email.bridgevine.io" "registry.bridgevine.io" "consul.tools.bridgevine.io" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done