#!/bin/bash
 
# Declare a string array with type
declare -a StringArray=( "cincinnatibellspecial.com" "b.cincinnatibellspecial.com" "cart.cincinnatibellspecial.com" "_b049c854e1851bc60385c55255f4e6d0.cart.cincinnatibellspecial.com" "www.cincinnatibellspecial.com" )
 
# Read the array values with space
for val in "${StringArray[@]}"; do
  nslookup -type=[CNAME] $val andy.ns.cloudflare.com | grep "** server can't find" | awk '{print $5}' > errorCNAME.txt 
done