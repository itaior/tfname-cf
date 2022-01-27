#!/usr/bin/env python3

import argparse
from threading import activeCount
import jinja2
import re
import boto3
import os

AWS_ACCOUNTID="6995"

resources = {
    'A': {},
    'AAAA': {},
    'CNAME': {},
    'MX': {},
    'SRV': {},
    'TXT': {},
    'NS': {}
}

def createResourceNameFromRecord(record):
    if record['Name'].endswith('.'):
        name = record['Name'][0:-1].replace('.', '_')
    else:
        name = record['Name'].replace('.', '_')
    if re.match(pattern=r'^\d', string=name):
        name = '_{}'.format(name)
    if record['Name'].startswith('\\052'):
        name = record['Name'].replace('\\052', 'star')
    return name

def fixRecordName(name):
    if name.startswith('\\052'):
        recordName = name.replace('\\052', '*')
    else:
        recordName = name
        
    if recordName.endswith('.'):
        recordName = recordName[0:-1]

    # if 2 means that it must be the parrent zone so we dont need any change
    if len(recordName.split('.')) == 2:
        pass
    # else means we have more than 1 subdomain so we will add the subdomains name for example test.tikal.updater.com ->
    # the name of the record will be test.tikal -> we will strip the last 2 names
    else:
        subDomainRecordName = ""
        for i in range(0, len(recordName.split('.'))-2):
            subDomainRecordName = subDomainRecordName +"."+ recordName.split('.')[i]
        # set records name after the loop
        recordName = subDomainRecordName[1:]
    return recordName

def removeDotFromEnd(value):
    if value.endswith('.'):
        value=value[0:-1]
    return value


def a(record):
    # match = re.match(A, record)
    print(record)
    match = (record['Type'] == 'A')
    if match:
        resource = createResourceNameFromRecord(record)
        if resource in resources['A']:
            return False
        recordName = fixRecordName(record['Name'])
        if 'ResourceRecords' in record:
            resources['A'][resource] = {
                'name': recordName,
                'ttl': 1,
                'value': removeDotFromEnd(record['ResourceRecords'][0]['Value'])
            }
        elif 'AliasTarget' in record:
            resources['A'][resource] = {
                'name': recordName,
                'ttl': "##TODO",
                'value':removeDotFromEnd(record['AliasTarget']['DNSName'])
            }   
        return True
    return False


def aaaa(record):
    match = (record['Type'] == 'AAAA')
    if match:
        resource = createResourceNameFromRecord(record)
        if resource in resources['AAAA']:
            return False
        recordName = fixRecordName(record['Name'])
        if 'ResourceRecords' in  record:      
            resources['AAAA'][resource] = {
                'name': recordName,
                'ttl': 1,
                'value': removeDotFromEnd(record['ResourceRecords'][0]['Value'])
            }
        elif 'AliasTarget' in record:
            resources['AAAA'][resource] = {
                'name': recordName,
                'ttl': "##TODO",
                'value': removeDotFromEnd(record['AliasTarget']['DNSName'])
            }  
        return True
    return False


def cname(record):
    # match = re.match(CNAME, record)
    match = (record['Type'] == 'CNAME')
    if match:
        resource = createResourceNameFromRecord(record)
        if resource in resources['CNAME']:
            return False
        recordName = fixRecordName(record['Name'])
        if 'ResourceRecords' in  record:     
            resources['CNAME'][resource] = {
                'name': recordName,
                'ttl': 1,
                'value': removeDotFromEnd(record['ResourceRecords'][0]['Value'])
            }  
        elif 'AliasTarget' in record:
            resources['CNAME'][resource] = {
                'name': recordName,
                'ttl': "##TODO",
                'value': removeDotFromEnd(record['AliasTarget']['DNSName'])
            }   
        return True
    return False


def mx(record):
    # match = re.match(MX, record)
    match = (record['Type'] == 'MX')
    if match:
        resource = createResourceNameFromRecord(record)
        if resource in resources['MX']:
            return False
        recordName = fixRecordName(record['Name'])
        x = int(len(record['ResourceRecords']))
        if x == 1:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()

            resources['MX'][resource] = {
                'name': recordName,
                'ttl': 1,
                'priority1': setPV[0],
                'value1': setPV[1],
                'priority2': "##TODO",
                'value2': "##TODO"
            }
        elif x == 2:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()  

            resources['MX'][resource] = {
                'name': recordName,
                'ttl': 1,
                'priority1': setPV[0],
                'priority2': setPV2[0],
                'value1': setPV[1],
                'value2': setPV2[1]
                }
        elif x == 3:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()
            setPV3 = record['ResourceRecords'][1]['Value'].split() 

            resources['MX'][resource] = {
                'name': recordName,
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
        resource = createResourceNameFromRecord(record)
        if resource in resources['TXT']:
            return False
        recordName = fixRecordName(record['Name'])
        value = record['ResourceRecords'][0]['Value'].replace('"', '')
        if re.match(r'.*DKIM', value):
            value = '; '.join(re.sub(pattern=r'\s+|\\;', repl='', string=value).split(';')).strip()
        # Silently ignore TXT records with empty string values as not supported by CloudFlare
        if not value:
            return True
        resources['TXT'][resource] = {
            'name': recordName,
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
        resource = createResourceNameFromRecord(record)
        if resource in resources['NS']:
            return False
        recordName = fixRecordName(record['Name'])
      # check the number of values in the ns record
        x = int(len(record['ResourceRecords']))
        if x == 4:
            resources['NS'][resource] = {
                'name': recordName,
                'ttl': 1,
                'value1': removeDotFromEnd(record['ResourceRecords'][0]['Value']),
                'value2': removeDotFromEnd(record['ResourceRecords'][1]['Value']),
                'value3': removeDotFromEnd(record['ResourceRecords'][2]['Value']),
                'value4': removeDotFromEnd(record['ResourceRecords'][3]['Value'])
                }
        elif x == 2:           
            resources['NS'][resource] = {
                'name': recordName,
                'ttl': 1,
                'value1': removeDotFromEnd(record['ResourceRecords'][0]['Value']),
                'value2': removeDotFromEnd(record['ResourceRecords'][1]['Value']),
                'value3': "##TODO",
                'value4': "##TODO"
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
        '-id',
        '--account_id',
        help='cloudlfare account id',
        default=str(),
        required=True,
        type=str
    )
    parser.add_argument(
        '-ns',
        '--ns_record',
        help='cloudlfare ns record, required for nslookup testing. Example Record: "guy.ns.cloudflare.com"',
        default=str(),
        required=True,
        type=str
    )
    return parser

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

def render(zone, rs, zoneName, account_id, cloudflare_ns_record):
    env = jinja2.Environment(loader=jinja2.PackageLoader('terraform_named_cloudflare', 'templates'))
    # # variables.tf
    # template = env.get_template('variables.tf.j2')
    # with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/variables.tf', 'w') as target:
    #     target.write(template.render(cloudflare_zone_name=zoneName))

    # main.tf
    template = env.get_template('main.tf.j2')
    with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/main.tf', 'w') as target:
        target.write(template.render(account_id=account_id, zoneName=zoneName))

    # cloudflareZone.tf
    template = env.get_template('cloudflareZone.tf.j2')
    terrafromResource=zone["Name"][0:-1].replace('.', '_')
    with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/zone.tf', 'w') as target:
        target.write(template.render(terrafromResource=terrafromResource, cloudflare_zone_name=zone["Name"][0:-1]))

        # records                
    for item in resources:
        if not len(resources[item]) == 0:
            template = env.get_template('{}.tf.j2'.format(item))
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/records.tf'.format(item), 'a') as target:
                target.write(template.render(resources=resources[item], terrafromResource=terrafromResource))

    # countRecords.txt
    recordA         = len(resources['A'])
    recordAAAA      = len(resources['AAAA'])
    recordCANME     = len(resources['CNAME'])
    recordMX        = len(resources['MX'])
    recordSRV       = len(resources['SRV'])
    recordTXT       = len(resources['TXT'])
    recordNS        = len(resources['NS'])
    recordsCreated  = recordA + recordAAAA + recordCANME + recordMX + recordSRV + recordTXT + recordNS
    awsArecord      = 0
    awsAAAArecord   = 0
    awsMXrecord     = 0
    awsTXTrecord    = 0
    awsCNAMErecord  = 0
    awsSRVrecord    = 0
    awsNSrecord     = 0
    for i in rs['ResourceRecordSets']:
        if i['Type'] == 'A':
            awsArecord += 1
        elif i['Type'] == 'NS':
            awsNSrecord += 1
        elif i['Type'] == 'AAAA':
            awsAAAArecord += 1
        elif i['Type'] == 'MX':
            awsMXrecord += 1
        elif i['Type'] == 'TXT':
            awsTXTrecord += 1
        elif i['Type'] == 'CNAME':
            awsCNAMErecord += 1
        elif i['Type'] == 'SRV':
            awsSRVrecord += 1

    template = env.get_template('countRecords.txt.j2')
    with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/countRecords.txt', 'w') as target:
        target.write(template.render(recordsCreated=recordsCreated, recordA=recordA, recordAAAA=recordAAAA,
        recordCANME=recordCANME, recordMX=recordMX, recordSRV=recordSRV, recordTXT=recordTXT, 
        recordNS=recordNS, awsArecord=awsArecord, awsAAAArecord=awsAAAArecord, awsMXrecord=awsMXrecord, 
        awsTXTrecord=awsTXTrecord, awsCNAMErecord=awsCNAMErecord, awsSRVrecord=awsSRVrecord, awsNSrecord=awsNSrecord,
        rs=(len(rs['ResourceRecordSets']))))
    
    # 0 subzones
    if recordNS == 0 and len(zoneName.split('_')) == 2:
        with open("./"+AWS_ACCOUNTID+'/'+AWS_ACCOUNTID+'_noSubZones.txt', 'a') as target:
            target.write(zoneName.replace('_', '.') + "\n")
    else:
        with open("./"+AWS_ACCOUNTID+'/'+AWS_ACCOUNTID+'_zonesWithSubDomains.txt', 'a') as target:
            target.write(zoneName.replace('_', '.') + "\n")

    # nslookup                
    for item in resources:
        # remove zone name from dictinary
        if  resources[item].get(zone['Name'].replace('.', '_')):
            resources[item].pop(zone['Name'].replace('.', '_'))
        # create file only for the necessary records
        if not len(resources[item]) == 0:
            template = env.get_template('nslookup{}.sh.j2'.format(item))
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/error/nslookup{}.sh'.format(item), 'a') as target:
                target.write(template.render(resources=resources[item], parentZone=zone['Name'][0:-1], cloudflare_ns_record=cloudflare_ns_record, space=" "))


def main():
    args = parse_arguments().parse_args()
    account_id = args.account_id
    cloudflare_ns_record = args.ns_record
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
            zoneName=zone["Name"].replace('.', '_')
            # silce the last '_' from the folder name
            zoneName=zoneName[0:-1]
            if os.path.exists("./"+AWS_ACCOUNTID+"/"+zoneName):
                pass
            else:
                os.mkdir("./"+AWS_ACCOUNTID+"/"+zoneName)
            if os.path.exists("./"+AWS_ACCOUNTID+"/"+zoneName+"/error"):
                pass
            else:
                os.mkdir("./"+AWS_ACCOUNTID+"/"+zoneName+"/error")
            parse_zone(zone, rs)
            render(zone, rs, zoneName, account_id, cloudflare_ns_record)
            # terraform fmt check
            os.system('cd ./'+AWS_ACCOUNTID+'/'+zoneName+' && terraform fmt && cd -')
            # empty resources dict for new zone
            for i in resources:
                resources[i].clear()


if __name__ == '__main__':
    main()


# {'ResponseMetadata': {'RequestId': 'a45a9681-b8c5-4b07-ada4-cf012a69e5ac',
#   'HTTPStatusCode': 200,
#   'HTTPHeaders': {'x-amzn-requestid': 'a45a9681-b8c5-4b07-ada4-cf012a69e5ac',
#    'content-type': 'text/xml',
#    'content-length': '919',
#    'date': 'Thu, 27 Jan 2022 10:53:34 GMT'},
#   'RetryAttempts': 0},
#  'ResourceRecordSets': [{'Name': 'prod.bridgevine.io.',
#    'Type': 'NS',
#    'TTL': 172800,
#    'ResourceRecords': [{'Value': 'ns-1664.awsdns-16.co.uk.'},
#     {'Value': 'ns-367.awsdns-45.com.'},
#     {'Value': 'ns-859.awsdns-43.net.'},
#     {'Value': 'ns-1025.awsdns-00.org.'}]},
#   {'Name': 'prod.bridgevine.io.',
#    'Type': 'SOA',
#    'TTL': 900,
#    'ResourceRecords': [{'Value': 'ns-1664.awsdns-16.co.uk. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400'}]}],
#  'IsTruncated': False,
#  'MaxItems': '300'}