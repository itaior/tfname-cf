#!/usr/bin/env python3

import argparse
import jinja2
import re
import boto3
import os

ACCOUNTID="9037"

resources = {
    'A': {},
    'AAAA': {},
    'CNAME': {},
    'MX': {},
    'SRV': {},
    'TXT': {},
    # 'NS': {}
}


def comment(record):
    # match = re.match(r'^;.*', record)
    if match:
        return True
    return False


def fix(name):
    name = name['Name'].replace('.', '_')
    if re.match(pattern=r'^\d', string=name):
        name = '_{}'.format(name)
    if name.startswith('*'):
        name = name.replace('*', 'star')
    return name


def a(record):
    # match = re.match(A, record)
    print(record)
    match = (record['Type'] == 'A')
    if match:
        resource = fix(record)
        if resource in resources['A']:
            return False
        if 'ResourceRecords' in  record:      
            resources['A'][resource] = {
                'name': record['Name'],
                'ttl': record['TTL'],
                'value': record['ResourceRecords'][0]['Value']
            }
        elif 'AliasTarget' in record:
            resources['A'][resource] = {
                'name': record['Name'],
                'ttl': "##TODO",
                'value': record['AliasTarget']['DNSName']
            }   
        return True
    return False


def aaaa(record):
    match = (record['Type'] == 'AAAA')
    if match:
        resource = fix(record)
        if resource in resources['AAAA']:
            return False
        if 'ResourceRecords' in  record:      
            resources['AAAA'][resource] = {
                'name': record['Name'],
                'ttl': record['TTL'],
                'value': record['ResourceRecords'][0]['Value']
            }
        elif 'AliasTarget' in record:
            resources['AAAA'][resource] = {
                'name': record['Name'],
                'ttl': "##TODO",
                'value': record['AliasTarget']['DNSName']
            }  
        return True
    return False


def cname(record):
    # match = re.match(CNAME, record)
    match = (record['Type'] == 'CNAME')
    if match:
        resource = fix(record)
        if resource in resources['CNAME']:
            return False
        if 'ResourceRecords' in  record:      
            resources['CNAME'][resource] = {
                'name': record['Name'],
                'ttl': record['TTL'],
                'value': record['ResourceRecords'][0]['Value']
            }  
        elif 'AliasTarget' in record:
            resources['CNAME'][resource] = {
                'name': record['Name'],
                'ttl': "##TODO",
                'value': record['AliasTarget']['DNSName']
            }   
        return True
    return False


def mx(record):
    # match = re.match(MX, record)
    match = False
    if match:
        resource = fix(record)
        if resource in resources['MX']:
            return False
        resources['MX'][resource] = {
            'name': match.group(1),
            'priority': match.group(3),
            'ttl': match.group(2),
            'value': match.group(4).strip('.')
        }
        return True
    return False


def srv(record):
    # match = re.match(SRV, record)
    match=False
    if match:
        resource = fix(match.group(1))
        if resource in resources['SRV']:
            return False
        resources['SRV'][resource] = {
            'data_name': match.group(4),
            'name': match.group(1),
            'port': match.group(8),
            'priority': match.group(6),
            'proto': match.group(3),
            'service': match.group(2),
            'target': match.group(9),
            'ttl': match.group(5),
            'weight': match.group(7)
        }
        return True
    return False


def txt(record):
    # match = re.match(TXT, record)
    match = (record['Type'] == 'TXT')
    if match:
        resource = fix(record)
        if resource in resources['TXT']:
            return False
        value = record['ResourceRecords'][0]['Value'].replace('"', '')
        if re.match(r'.*DKIM', value):
            value = '; '.join(re.sub(pattern=r'\s+|\\;', repl='', string=value).split(';')).strip()
        # Silently ignore TXT records with empty string values as not supported by CloudFlare
        if not value:
            return True
        resources['TXT'][resource] = {
            'name': record['Name'],
            'ttl': record['TTL'],
            'value': value
        }
        return True
    return False


def parse_arguments():
    """
    Function to handle argument parser configuration (argument definitions, default values and so on).
    :return: :obj:`argparse.ArgumentParser` object with set of configured arguments.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--zone-id',
        default=str(),
        help='Optional CloudFlare zone ID',
        type=str
    )
    parser.add_argument(
        '-n',
        '--zone-name',
        default=str(),
        help='Optional CloudFlare zone name',
        type=str
    )
    return parser


def parse_zone(data):
    for record in data['ResourceRecordSets']:
        print(record)
        # if not comment(record=record):
        if a(record=record):
            continue
        if aaaa(record=record):
            continue
        if cname(record=record):
            continue
        if mx(record=record):
            continue
        if srv(record=record):
            continue
        if txt(record=record):
            continue
        print(record)


def render(known_args, zone):
    env = jinja2.Environment(loader=jinja2.PackageLoader('terraform_named_cloudflare', 'templates'))
    template = env.get_template('variables.tf.j2')
    with open("./"+ACCOUNTID+"/"+zone["Name"]+'/variables.tf', 'w') as target:
        target.write(template.render(cloudflare_zone_id=known_args.zone_id, cloudflare_zone_name=known_args.zone_name))
    for item in resources:
        template = env.get_template('{}.tf.j2'.format(item))
        with open("./"+ACCOUNTID+"/"+zone["Name"]+'/{}.tf'.format(item), 'w') as target:
            target.write(template.render(resources=resources[item]))


def main():
    known_args, unknown_args = parse_arguments().parse_known_args()
    client = boto3.client('route53')
    hostedzone=client.list_hosted_zones()
    os.mkdir("./"+ACCOUNTID)
    for zone in hostedzone["HostedZones"]:
        if not zone["Config"]["PrivateZone"]:
            rs=client.list_resource_record_sets(HostedZoneId=zone["Id"])
            os.mkdir("./"+ACCOUNTID+"/"+zone["Name"])
            parse_zone(rs)
            render(known_args, zone)


if __name__ == '__main__':
    main()
