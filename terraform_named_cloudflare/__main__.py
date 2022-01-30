#!/usr/bin/env python3

import argparse
from threading import activeCount
import jinja2
import re
import boto3
import os

AWS_ACCOUNTID="6995"

# the resources dict will look like:
# resources = {
#    'A': {
#         resource {
#               name:VALUE, ttl:value, value:VALUE},
#          resource2 {
#               name:VALUE, ttl:value, value:VALUE}}
#    and so on for all the other lists with thier values
#    resource and resource2 will be equal to createResourceNameFromRecord(), which is always the record name the we parse "now"
#    we still needs another value called recordName becuase we do diffrent manipulation on it and use it in deffrent places
# }
resources = {
    'A': {},
    'AAAA': {},
    'CNAME': {},
    'MX': {},
    'SPF': {},
    'SRV': {},
    'TXT': {},
    'NS': {}
}

# sets the name of the recources in for example resources['A'][the name of the resource]
def createResourceNameFromRecord(record):
    if record['Name'].endswith('.'):
        name = record['Name'][0:-1].replace('.', '_')
    else:
        name = record['Name'].replace('.', '_')
    if re.match(pattern=r'^\d', string=name):
        name = '_{}'.format(name)
    if name.startswith('\\052'):
        name = name.replace('\\052', 'star')
    return name

# sets the of the name of the record
# removing the . at the end of the name
# changeing boto3 output of \052 back to star
# if subDomain - get only the subDomain name - remove the xxx.com from the name 
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

# remove trailing . for values
def removeDotFromEnd(value):
    if value.endswith('.'):
        value=value[0:-1]
    return value

# addes resources to resources['A'] 
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
            resources['CNAME'][resource] = {
                'name': recordName,
                'ttl': "1",
                'value':removeDotFromEnd(record['AliasTarget']['DNSName'])
            }   
        return True
    return False

# addes resources to resources['AAAA'] 
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
            resources['CNAME'][resource] = {
                'name': recordName,
                'ttl': "1",
                'value': removeDotFromEnd(record['AliasTarget']['DNSName'])
            }  
        return True
    return False

# addes resources to resources['CNAME'] 
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
                'ttl': "1",
                'value': removeDotFromEnd(record['AliasTarget']['DNSName'])
            }   
        return True
    return False

# addes resources to resources['MX'] 
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
                'priority2': "##TODO",
                'priority3': "##TODO",
                'priority4': "##TODO",
                'priority5': "##TODO",
                'value1': setPV[1],
                'value2': "##TODO",
                'value3': "##TODO",
                'value4': "##TODO",
                'value5': "##TODO"
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
                'priority3': "##TODO",
                'priority4': "##TODO",
                'priority5': "##TODO",
                'value1': setPV[1],
                'value2': setPV2[1],
                'value3': "##TODO",
                'value4': "##TODO",
                'value5': "##TODO"
                }
        elif x == 3:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()
            setPV3 = record['ResourceRecords'][2]['Value'].split() 

            resources['MX'][resource] = {
                'name': recordName,
                'ttl': 1,
                'priority1': setPV[0],
                'priority2': setPV2[0],
                'priority3': setPV3[0],
                'priority4': "##TODO",
                'priority5': "##TODO",
                'value1': setPV[1],
                'value2': setPV2[1],
                'value3': setPV3[1],
                'value4': "##TODO",
                'value5': "##TODO"
                }
        elif x == 4:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()
            setPV3 = record['ResourceRecords'][2]['Value'].split()
            setPV4 = record['ResourceRecords'][3]['Value'].split()

            resources['MX'][resource] = {
                'name': recordName,
                'ttl': 1,
                'priority1': setPV[0],
                'priority2': setPV2[0],
                'priority3': setPV3[0],
                'priority4': setPV4[0],
                'priority5': "##TODO",
                'value1': setPV[1],
                'value2': setPV2[1],
                'value3': setPV3[1],
                'value4': setPV4[1],
                'value5': "##TODO"
                }
        elif x == 5:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()
            setPV3 = record['ResourceRecords'][2]['Value'].split()
            setPV4 = record['ResourceRecords'][3]['Value'].split()
            setPV5 = record['ResourceRecords'][4]['Value'].split()

            resources['MX'][resource] = {
                'name': recordName,
                'ttl': 1,
                'priority1': setPV[0],
                'priority2': setPV2[0],
                'priority3': setPV3[0],
                'priority4': setPV4[0],
                'priority5': setPV5[0],
                'value1': setPV[1],
                'value2': setPV2[1],
                'value3': setPV3[1],
                'value4': setPV4[1],
                'value5': setPV5[1]
                }
        return True
    return False

# addes resources to resources['TXT'] 
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

# addes resources to resources['NS'] 
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

# addes resources to resources['SPF'] 
def spf(record):
    # match = re.match(A, record)
    print(record)
    match = (record['Type'] == 'SPF')
    if match:
        resource = createResourceNameFromRecord(record)
        value = record['ResourceRecords'][0]['Value'].replace('"', '')
        if re.match(r'.*DKIM', value):
            value = '; '.join(re.sub(pattern=r'\s+|\\;', repl='', string=value).split(';')).strip()
        if resource in resources['SPF']:
            return False
        recordName = fixRecordName(record['Name'])
        resources['SPF'][resource] = {
            'name': recordName,
            'ttl': 1,
            'value': value
        } 
        return True
    return False

# input parametes for script
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

# parsing through the records
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
        if txt(record=record):
            continue
        if spf(record=record):
            continue
        # exclude NS records of the zone we work on
        if record['Name'] != zone["Name"] and ns(record=record):
            continue
        print(record)

# render for all files
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
    # cloudflare_zone_name=zoneName - replacing the _ with .
    template = env.get_template('cloudflareZone.tf.j2')
    with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/zone.tf', 'w') as target:
        target.write(template.render(terrafromResource=zoneName, cloudflare_zone_name=zoneName.replace('_', '.')))

    # records                
    for item in resources:
        if not len(resources[item]) == 0:
            template = env.get_template('{}.tf.j2'.format(item))
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/records.tf', 'a') as target:
                target.write(template.render(resources=resources[item], terrafromResource=zoneName))

    # countRecords.txt
    recordA         = len(resources['A'])
    recordAAAA      = len(resources['AAAA'])
    recordCANME     = len(resources['CNAME'])
    recordMX        = len(resources['MX'])
    recordSRV       = len(resources['SRV'])
    recordTXT       = len(resources['TXT'])
    recordNS        = len(resources['NS'])
    recordSPF       = len(resources['SPF'])
    recordsCreated  = recordA + recordAAAA + recordCANME + recordMX + recordSRV + recordTXT + recordNS
    awsArecord      = 0
    awsAAAArecord   = 0
    awsMXrecord     = 0
    awsTXTrecord    = 0
    awsCNAMErecord  = 0
    awsSRVrecord    = 0
    awsNSrecord     = 0
    awsSPFrecord    = 0
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
        elif i['Type'] == 'SPF':
            awsSPFrecord += 1

    template = env.get_template('countRecords.txt.j2')
    with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/countRecords.txt', 'w') as target:
        target.write(template.render(recordsCreated=recordsCreated, recordA=recordA, recordAAAA=recordAAAA,
        recordCANME=recordCANME, recordMX=recordMX, recordSRV=recordSRV, recordTXT=recordTXT, 
        recordNS=recordNS, awsArecord=awsArecord, awsAAAArecord=awsAAAArecord, awsMXrecord=awsMXrecord, 
        awsTXTrecord=awsTXTrecord, awsCNAMErecord=awsCNAMErecord, awsSRVrecord=awsSRVrecord, awsNSrecord=awsNSrecord,
        awsSPFrecord=awsSPFrecord, recordSPF=recordSPF, rs=(len(rs['ResourceRecordSets']))))
    
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
                target.write(template.render(resources=resources[item], parentDomain=zoneName.replace('_', '.'), cloudflare_ns_record=cloudflare_ns_record, space=" "))


def main():
    # get input parameters
    args = parse_arguments().parse_args()
    account_id = args.account_id
    cloudflare_ns_record = args.ns_record
    
    # get zones list
    client = boto3.client('route53')
    hostedzone=client.list_hosted_zones()

    # check if folder exists
    if os.path.exists("./"+AWS_ACCOUNTID):
        pass
    else:
        os.mkdir("./"+AWS_ACCOUNTID)
    
    # filter out private domains
    for zone in hostedzone["HostedZones"]:
        if not zone["Config"]["PrivateZone"]:
            # get all the records from the zone
            rs=client.list_resource_record_sets(HostedZoneId=zone["Id"],MaxItems='2000')

            # set zone name
            zoneName=zone["Name"].replace('.', '_')
            # silce the last '_' from the folder name
            if zone['Name'].endswith('.'):
                zoneName=zoneName[0:-1]

            # check if folder exists
            if os.path.exists("./"+AWS_ACCOUNTID+"/"+zoneName):
                pass
            else:
                os.mkdir("./"+AWS_ACCOUNTID+"/"+zoneName)

            # check if folder exists
            if os.path.exists("./"+AWS_ACCOUNTID+"/"+zoneName+"/error"):
                pass
            else:
                os.mkdir("./"+AWS_ACCOUNTID+"/"+zoneName+"/error")
            
            # parsing through the records list
            parse_zone(zone, rs)

            # writing to files
            render(zone, rs, zoneName, account_id, cloudflare_ns_record)

            # terraform fmt check
            os.system('cd ./'+AWS_ACCOUNTID+'/'+zoneName+' && terraform fmt && cd -')

            # empty resources dict for new zone
            for i in resources:
                resources[i].clear()


if __name__ == '__main__':
    main()
