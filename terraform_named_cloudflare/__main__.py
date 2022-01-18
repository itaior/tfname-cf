#!/usr/bin/env python3

import argparse
import jinja2
import re
import boto3
import os

AWS_ACCOUNTID="Tikal"

index = {
  'A': {},
  'AAAA': {},
  'CNAME': {},
  'MX': {},
  'SRV': {},
  'TXT': {},
  'NS': {}
}

resources = {
    'A': {},
    'AAAA': {},
    'CNAME': {},
    'MX': {},
    'SRV': {},
    'TXT': {},
    'NS': {}
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
          # test and check duplicate records
        # if resource in index[record['Type']]:
        #   index[record['Type']][resource] += 1
        # else:
        #   index[record['Type']][resource] = 1
        # resource = f"{resource}{index[record['Type']][resource]}_"
        if 'ResourceRecords' in  record:      
            resources['A'][resource] = {
                'name': record['Name'],
                'ttl': 1,
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
          # test and check duplicate records
        # if resource in index[record['Type']]:
        #   index[record['Type']][resource] += 1
        # else:
        #   index[record['Type']][resource] = 1
        # resource = f"{resource}{index[record['Type']][resource]}_"      
        if 'ResourceRecords' in  record:      
            resources['AAAA'][resource] = {
                'name': record['Name'],
                'ttl': 1,
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
          # test and check duplicate records
        # if resource in index[record['Type']]:
        #   index[record['Type']][resource] += 1
        # else:
        #   index[record['Type']][resource] = 1
        # resource = f"{resource}{index[record['Type']][resource]}_"      
        if 'ResourceRecords' in  record:      
            resources['CNAME'][resource] = {
                'name': record['Name'],
                'ttl': 1,
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
    match = (record['Type'] == 'MX')
    if match:
        resource = fix(record)
        if resource in resources['MX']:
          return False
          # test and check duplicate records
        # if resource in index[record['Type']]:
        #   index[record['Type']][resource] += 1
        # else:
        #   index[record['Type']][resource] = 1
        # resource = f"{resource}{index[record['Type']][resource]}_"      
        x = int(len(record['ResourceRecords']))
        if x == 1:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()

            resources['MX'][resource] = {
                'name': record['Name'],
                'ttl': 1,
                'priority1': setPV[0],
                'value1': setPV[1],
                'priority2': "#TODO",
                'value2': "#TODO"
            }
        elif x == 2:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()  

            resources['MX'][resource] = {
                'name': record['Name'],
                'ttl': 1,
                'priority1': setPV[0],
                'priority2': setPV2[0],
                'value1': setPV[1],
                'value2': setPV2[1]
                }
        return True
    return False

def srv(record):
    # match = re.match(SRV, record)
    match= False
    if match:
        resource = fix(match.group(1))
        if resource in resources['SRV']:
          return False
          # test and check duplicate records
        # if resource in index[record['Type']]:
        #   index[record['Type']][resource] += 1
        # else:
        #   index[record['Type']][resource] = 1
        # resource = f"{resource}{index[record['Type']][resource]}_"
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
          # test and check duplicate records
        # if resource in index[record['Type']]:
        #   index[record['Type']][resource] += 1
        # else:
        #   index[record['Type']][resource] = 1
        # resource = f"{resource}{index[record['Type']][resource]}_"
        value = record['ResourceRecords'][0]['Value'].replace('"', '')
        if re.match(r'.*DKIM', value):
            value = '; '.join(re.sub(pattern=r'\s+|\\;', repl='', string=value).split(';')).strip()
        # Silently ignore TXT records with empty string values as not supported by CloudFlare
        if not value:
            return True
        resources['TXT'][resource] = {
            'name': record['Name'],
            'ttl': 1,
            'value': value
        }
        return True
    return False

def ns(record):
    # match = re.match(NS, record)
    print(record)
    match = (record['Type'] == 'NS')
    if match:
        resource = fix(record)
        if resource in resources['NS']:
          return False
          # test and check duplicate records
        # if resource in index[record['Type']]:
        #   index[record['Type']][resource] += 1
        # else:
        #   index[record['Type']][resource] = 1
        # resource = f"{resource}{index[record['Type']][resource]}_"
      # check the number of values in the ns record
        x = int(len(record['ResourceRecords']))
        if x == 4:
            resources['NS'][resource] = {
                'name': record['Name'],
                'ttl': 1,
                'value1': record['ResourceRecords'][0]['Value'],
                'value2': record['ResourceRecords'][1]['Value'],
                'value3': record['ResourceRecords'][2]['Value'],
                'value4': record['ResourceRecords'][3]['Value']
                }
        elif x == 2:           
            resources['NS'][resource] = {
                'name': record['Name'],
                'ttl': 1,
                'value1': record['ResourceRecords'][0]['Value'],
                'value2': record['ResourceRecords'][1]['Value'],
                'value3': "#TODO",
                'value4': "#TODO"
                }
        return True
    return False

def parse_zone(zone, rs):
    for record in rs['ResourceRecordSets']:
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
        # exclude NS records of the zone we work on
        if record['Name'] != zone["Name"] and ns(record=record):
            continue
        print(record)

def render(zone, rs, zoneName):
    env = jinja2.Environment(loader=jinja2.PackageLoader('terraform_named_cloudflare', 'templates'))
    # # variables.tf
    # template = env.get_template('variables.tf.j2')
    # with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/variables.tf', 'w') as target:
    #     target.write(template.render(cloudflare_zone_name=zoneName))
    # cloudflareZone.tf
    template = env.get_template('cloudflareZone.tf.j2')
    resourcename=zone["Name"].replace('.', '_')
    with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/cloudflareZone.tf', 'w') as target:
        target.write(template.render(resourcename=resourcename, cloudflare_zone_name=zone["Name"]))
    # records                
    for item in resources:
        if not len(resources[item]) == 0:
            template = env.get_template('{}.tf.j2'.format(item))
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/{}.tf'.format(item), 'w') as target:
                target.write(template.render(resources=resources[item], resourcename=resourcename))
    # countRecords.txt
    recordA=len(resources['A'])
    recordAAAA=len(resources['AAAA'])
    recordCANME=len(resources['CNAME'])
    recordMX=len(resources['MX'])
    recordSRV=len(resources['SRV'])
    recordTXT=len(resources['TXT'])
    recordNS=len(resources['NS'])
    recordsCreated = recordA + recordAAAA + recordCANME + recordMX + recordSRV + recordTXT + recordNS
    template = env.get_template('countRecords.txt.j2')
    with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/countRecords.txt', 'w') as target:
        target.write(template.render(recordsCreated=recordsCreated, recordA=recordA, recordAAAA=recordAAAA,recordCANME=recordCANME, recordMX=recordMX, recordSRV=recordSRV, recordTXT=recordTXT, recordNS=recordNS, rs=(len(rs['ResourceRecordSets']))))

def main():
    client = boto3.client('route53')
    hostedzone=client.list_hosted_zones()
    if os.path.exists("./"+AWS_ACCOUNTID):
        pass
    else:
        os.mkdir("./"+AWS_ACCOUNTID)
    for zone in hostedzone["HostedZones"]:
        if not zone["Config"]["PrivateZone"]:
            rs=client.list_resource_record_sets(HostedZoneId=zone["Id"],MaxItems='2000')
            # set correct name for terraform module
            zoneName=zone["Name"].replace('.', '-')
            # silce the last - from the folder name
            zoneName=zoneName[0:-1]
            if os.path.exists("./"+AWS_ACCOUNTID+"/"+zoneName):
                pass
            else:
                os.mkdir("./"+AWS_ACCOUNTID+"/"+zoneName)
            parse_zone(zone, rs)
            render(zone, rs, zoneName)
            # empty resources dict for new zone
            for i in resources:
                resources[i].clear()
            # empty resources dict for new zone
            for i in index:
                index[i].clear()

if __name__ == '__main__':
    main()
