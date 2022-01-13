# This project was forked from https://github.com/pa-yourserveradmin-com/terraform-named-cloudflare

# terraform-named-cloudflare

Python module and tool to easily convert Bind9 (named) zones into Terraform
CloudFlare provider records definitions.

This module parses Bind9 (named) zone file and generates Terraform code with
CloudFlare resources definitions.

To make the result code organized, code separated based on DNS records types.

## Installation

To install our version of this project, just clone the repository and install the
module:

```bash
git clone 
cd terraform-named-cloudflare
python3 setup.py install
```

## Usage

* export the aws account 
export AWS_PROFILE=<PROFILE_NAME>

```bash
terraform-named-cloudflare
```

Since not all records need to be converted in Terraform code, the script ignores
some of them and just prints ignored records to standard output to provide ability
review them and add manually.

## Requirements

There are no specific requirements except a few weel-known and widelly used Python
modules listed in the [requirements.txt](requirements.txt) and automatically
installed with module.

## Limitations

The module does not understand DNS RRD records and always will create only one
resource with the same name. The rest will be ignored and printed to standard
output for review and manual changes in Terraform code.

## Supported DNS records types

Currently this module supports the next types of DNS records:

- A
- AAAA
- CNAME
- MX
- SRV
- TXT
- NS

Other types of DNS records can be added based on the need. Also, contrinutions
are always welcome.
