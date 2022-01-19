# This project was originaly forked from https://github.com/pa-yourserveradmin-com/terraform-named-cloudflare

# terraform-named-cloudflare

Python tool to easily get all the aws route53 zones under your account into Terraform
CloudFlare provider records definitions.

This module parses each aws route53 zone and generates Terraform resources as Cloudflare terrafrom records.

To make the result code organized, code separated based on DNS records types.

## Installation

To install our version of this project, just clone the repository and install the
module:

```bash
git clone git@github.com:itaior/tfname-cf.git
cd terraform-named-cloudflare
python3 setup.py install
```

## Usage

* export the aws account 
export AWS_PROFILE=<PROFILE_NAME>

```bash
terraform-named-cloudflare -id <CLOUDFLARE_ACCOUNT_ID> -ns <CLOUDFLARE_NS_RECORDS>
```

Since not all records need to be converted in Terraform code, the tool ignores
some of them, for example we are excluding the top NS record and the SOA record.
In the countRecord.txt we will see 2 records missing. (check Limitations)

## Requirements

There are no specific requirements except a few weel-known and widelly used Python
modules listed in the [requirements.txt](requirements.txt) and automatically
installed with module.

## Limitations
There some edge cases that might be missed, like MX record with more than 2 values.
In order to over come those cases we create a summry file that will compare the records
created and the actual records in the aws route53 zone.

For example:
׳׳׳
    A                       = "108"
    AAAA                    = "0" 
    CNAME                   = "14" 
    MX                      = "0"
    SRV                     = "0"
    TXT                     = "4"
    NS                      = "0"
  -------------------------------------------------
  total records Created   = "126"
    
  total recrds in AWS     = "129"
  -------------------------------------------------
    A                       = "108"
    AAAA                    = "0" 
    CNAME                   = "14" 
    MX                      = "1"
    SRV                     = "0"
    TXT                     = "4"
    NS                      = "1"
׳׳׳

In this case we can see that the tool missed one edge case of MX record and there for we should check this case in the our
aws zone. 
Becuase we exclude the top NS record and the SOA record a deficit of 2 record means that all records were 
parased and were added to the Terraform files.

## Supported DNS records types

Currently this module supports the next types of DNS records:

- A
- AAAA
- CNAME
- MX
- TXT
- NS

Other types of DNS records can be added based on the need. Also, contrinutions
are always welcome.
