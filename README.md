# This project was originaly forked from 
https://github.com/pa-yourserveradmin-com/terraform-named-cloudflare

# terraform-named-cloudflare

Our Python tool easily gets all the route53 zones and recods of spesific aws account 
and parse them into Terraform cloudflare resources.

In addition the tool will create tests to validate the new records in cloudflare 
using nslookup.

To make the result code organized, code separated based on DNS records types.
If you would prefer to use one file for all of your records swith branch to oneTF,
where the records will be orderd by type.

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
```bash
export AWS_PROFILE=<PROFILE_NAME>
```
* cli command to run the tool

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
There are some edge cases that might be missed.
In order to over come those cases we created a summry file, named 'countRecords.txt', that will compare the records
that were templated as terraform cloudflare resources with the actual records in the aws route53 zone.

For example:
```
    A                   = "108"
    AAAA                = "0" 
    CNAME               = "14" 
    MX                  = "0"
    SPF                 = "0"
    TXT                 = "4"
    NS                  = "0"
  -------------------------------------------------
  total records Created = "127"
    
  total recrds in AWS   = "129"
  -------------------------------------------------
    A                   = "108"
    AAAA                = "0" 
    CNAME               = "14" 
    MX                  = "1"
    SPF                 = "0"
    TXT                 = "4"
    NS                  = "1"
```

Becuase we exclude the top level NS record and the SOA, a deficit of 2 record means that all records were 
parased and created as terraform resources.

## Validation
There are some edge cases that might be missed, when creating the records.
That is why we compare the records that were created in your accout cloudflare 
to the value of the current known records in the global DNS server.

curently SPF validation is not complete.

**We always recommend a human validation as well**

## Supported DNS records types

Currently this module supports the next types of DNS records:

- A
- AAAA
- CNAME
- MX
- SPF
- TXT
- NS

Other types of DNS records can be added based on the need. Also, contrinutions
are always welcome.
