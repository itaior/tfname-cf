#!/usr/bin/env python3

##TODO set imports for TXT MX NS
##TODO jinja templates to spesific folders

import argparse
from threading import activeCount
import jinja2
import re
import boto3
import os

globals
AWS_ACCOUNTID="1111"

# used to count records that were created
resources = {
    'A': {},
    'AAAA': {},
    'CNAME': {},
    'MX': {},
    'NS': {},
    'SPF': {},
    'SRV': {},
    'TXT': {},
}

def set_ZoneName(zone):
    # set zone name
    zoneName=zone['Name'].replace('.', '_')
    # silce the last '_' from the folder name
    if zone['Name'].endswith('.'):
        zoneName=zoneName[0:-1]
    return zoneName

# sets the name of the recources in for example resources['A'][the name of the resource]
def set_ResourceName(record):
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
def set_RecordName(name):
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

def set_TXTValue(inpurt_value):
    value = inpurt_value.replace('"', '')
    if re.match(r'.*DKIM', value):
        value = '; '.join(re.sub(pattern=r'\s+|\\;', repl='', string=value).split(';')).strip()
    return value

def render_single_value_records(temp_path, zoneName, recordName, ttl, value, resource):
    env = jinja2.Environment(loader=jinja2.PackageLoader('terraform_named_cloudflare', 'templates'))
    template = env.get_template(f'{temp_path}.tf.j2')
    with open(f'./{AWS_ACCOUNTID}/{zoneName}/{temp_path}.tf', 'a') as target:
        target.write(template.render(name=recordName, ttl=ttl, value=value, 
        terrafromResource=resource, zone_id=zoneName))

def render_MX_records(temp_path, zoneName, recordName, ttl, resource,
    value1, praiority1, value2="", praiority2="", value3="", praiority3="", 
    value4="", praiority4="", value5="", praiority5=""):
    env = jinja2.Environment(loader=jinja2.PackageLoader('terraform_named_cloudflare', 'templates'))
    template = env.get_template(f'{temp_path}.tf.j2')
    with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/MX.tf', 'a') as target:
        target.write(template.render(name=recordName, ttl=ttl, 
                value1=value1, priority1=praiority1, 
                value2=value2, priority2=praiority2,
                value3=value3, priority3=praiority3,
                value4=value4, priority4=praiority4,
                value5=value5, priority5=praiority5,
                terrafromResource=resource, zone_id=zoneName)) 

def render_NS_records(temp_path, zoneName, recordName, ttl, resource, 
    value1, value2="", value3="", value4=""):

    env = jinja2.Environment(loader=jinja2.PackageLoader('terraform_named_cloudflare', 'templates'))
    template = env.get_template(f'{temp_path}.tf.j2')
    with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/NS.tf', 'a') as target:
        target.write(template.render(name=recordName, ttl=ttl, 
        value1=value1, value2=value2, value3=value3,
        value4=value4,
        terrafromResource=resource, zone_id=zoneName)) 

def render_TXT_records(temp_path, zoneName, recordName, ttl, resource,
    value1, value2="", value3="", 
    value4="", value5="", value6="", 
    value7="", value8="", value9="", 
    value10=""):

    env = jinja2.Environment(loader=jinja2.PackageLoader('terraform_named_cloudflare', 'templates'))
    template = env.get_template(f'{temp_path}.tf.j2')
    with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/TXT.tf', 'a') as target:
        target.write(template.render(name=recordName, ttl=ttl, 
        value1=value1, value2=value2, value3=value3,
        value4=value4, value5=value5, value6=value6,
        value7=value7, value8=value8, value9=value9,
        value10=value10,
        terrafromResource=resource, zone_id=zoneName)) 

# addes resources to resources['A'] 
def a(zoneName, record):
    # match = re.match(A, record)
    print(record)
    match = (record['Type'] == 'A')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        if 'ResourceRecords' in record:
            # add to A record dictinary
            resources['A'][resource] = { 'name': recordName }

            render_single_value_records("A", zoneName, recordName, 1, 
                removeDotFromEnd(record['ResourceRecords'][0]['Value']), resource)
        elif 'AliasTarget' in record:
            # add to CNAME record dictinary
            resources['CNAME'][resource] = { 'name': recordName }

            render_single_value_records("CNAME", zoneName, recordName, 1, 
                removeDotFromEnd(record['AliasTarget']['DNSName']), resource)   
        return True
    return False

# addes resources to resources['AAAA'] 
def aaaa(zoneName, record):
    match = (record['Type'] == 'AAAA')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        if 'ResourceRecords' in  record:
            # add to AAAA record dictinary
            resources['AAAA'][resource] = { 'name': recordName }                 
            render_single_value_records("AAAA", zoneName, recordName, 1, 
                removeDotFromEnd(record['ResourceRecords'][0]['Value']), resource)
        elif 'AliasTarget' in record:
            # add to CNAME record dictinary
            resources['CNAME'][resource] = { 'name': recordName }
            render_single_value_records("CNAME", zoneName, recordName, 1, 
                removeDotFromEnd(record['AliasTarget']['DNSName']), resource) 
        return True
    return False

# addes resources to resources['CNAME'] 
def cname(zoneName, record):
    # match = re.match(CNAME, record)
    match = (record['Type'] == 'CNAME')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        # add to CNAME record dictinary
        resources['CNAME'][resource] = { 'name': recordName }  
        if 'ResourceRecords' in  record:   
            render_single_value_records("CNAME", zoneName, recordName, 1, 
                removeDotFromEnd(record['ResourceRecords'][0]['Value']), resource)
        elif 'AliasTarget' in record:
            render_single_value_records("CNAME", zoneName, recordName, 1, 
                removeDotFromEnd(record['AliasTarget']['DNSName']), resource)
        return True
    return False

# addes resources to resources['MX'] 
def mx(zoneName, record):
    # match = re.match(MX, record)
    match = (record['Type'] == 'MX')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        resources['MX'][resource] = { 'name': recordName }  
        x = int(len(record['ResourceRecords']))
        if x == 1:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            
            render_MX_records("MX", zoneName, recordName, 1, resource, 
                removeDotFromEnd(setPV[1]), setPV[0])

        elif x == 2:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()  

            render_MX_records("MX2", zoneName, recordName, 1, resource, 
                removeDotFromEnd(setPV[1]), setPV[0],
                removeDotFromEnd(setPV2[1]), setPV2[0])

        elif x == 3:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()
            setPV3 = record['ResourceRecords'][2]['Value'].split() 

            render_MX_records("MX3", zoneName, recordName, 1, resource, 
                removeDotFromEnd(setPV[1]), setPV[0],
                removeDotFromEnd(setPV2[1]), setPV2[0], 
                removeDotFromEnd(setPV3[1]), setPV3[0])

        elif x == 4:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()
            setPV3 = record['ResourceRecords'][2]['Value'].split()
            setPV4 = record['ResourceRecords'][3]['Value'].split()

            render_MX_records("MX4", zoneName, recordName, 1, resource, 
                removeDotFromEnd(setPV[1]), setPV[0],
                removeDotFromEnd(setPV2[1]), setPV2[0], 
                removeDotFromEnd(setPV3[1]), setPV3[0],
                removeDotFromEnd(setPV4[1]), setPV4[0])

        elif x == 5:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()
            setPV3 = record['ResourceRecords'][2]['Value'].split()
            setPV4 = record['ResourceRecords'][3]['Value'].split()
            setPV5 = record['ResourceRecords'][4]['Value'].split()

            render_MX_records("MX5", zoneName, recordName, 1, resource, 
                removeDotFromEnd(setPV[1]), setPV[0],
                removeDotFromEnd(setPV2[1]), setPV2[0], 
                removeDotFromEnd(setPV3[1]), setPV3[0],
                removeDotFromEnd(setPV4[1]), setPV4[0],
                removeDotFromEnd(setPV5[1]), setPV5[0])
        return True
    return False



# addes resources to resources['TXT'] 
def txt(zoneName, record):
    # match = re.match(TXT, record)
    match = (record['Type'] == 'TXT')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        resources['TXT'][resource] = { 'name': recordName } 

        if (len(record['ResourceRecords'])) == 1:
            value1 = set_TXTValue(record['ResourceRecords'][0]['Value'].replace('"', ''))

            render_TXT_records("TXT", zoneName, recordName, 1, resource,
                value1=value1)

        elif (len(record['ResourceRecords'])) == 2:
            value1 = set_TXTValue(record['ResourceRecords'][0]['Value'].replace('"', ''))
            value2 = set_TXTValue(record['ResourceRecords'][1]['Value'].replace('"', ''))

            render_TXT_records("TXT2", zoneName, recordName, 1, resource,
                value1=value1, value2=value2)

        elif (len(record['ResourceRecords'])) == 3:
            value1 = set_TXTValue(record['ResourceRecords'][0]['Value'].replace('"', ''))
            value2 = set_TXTValue(record['ResourceRecords'][1]['Value'].replace('"', ''))
            value3 = set_TXTValue(record['ResourceRecords'][2]['Value'].replace('"', ''))

            render_TXT_records("TXT3", zoneName, recordName, 1, resource,
                value1=value1, value2=value2, value3=value3)

        elif (len(record['ResourceRecords'])) == 4:
            value1 = set_TXTValue(record['ResourceRecords'][0]['Value'].replace('"', ''))
            value2 = set_TXTValue(record['ResourceRecords'][1]['Value'].replace('"', ''))
            value3 = set_TXTValue(record['ResourceRecords'][2]['Value'].replace('"', ''))
            value4 = set_TXTValue(record['ResourceRecords'][3]['Value'].replace('"', ''))

            render_TXT_records("TXT4", zoneName, recordName, 1, resource,
                value1=value1, value2=value2, value3=value3, 
                value4=value4)

        elif (len(record['ResourceRecords'])) == 5:
            value1 = set_TXTValue(record['ResourceRecords'][0]['Value'].replace('"', ''))
            value2 = set_TXTValue(record['ResourceRecords'][1]['Value'].replace('"', ''))
            value3 = set_TXTValue(record['ResourceRecords'][2]['Value'].replace('"', ''))
            value4 = set_TXTValue(record['ResourceRecords'][3]['Value'].replace('"', ''))
            value5 = set_TXTValue(record['ResourceRecords'][4]['Value'].replace('"', ''))

            render_TXT_records("TXT5", zoneName, recordName, 1, resource,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5)

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 5_TXT \n")

        elif (len(record['ResourceRecords'])) == 6:
            value1 = set_TXTValue(record['ResourceRecords'][0]['Value'].replace('"', ''))
            value2 = set_TXTValue(record['ResourceRecords'][1]['Value'].replace('"', ''))
            value3 = set_TXTValue(record['ResourceRecords'][2]['Value'].replace('"', ''))
            value4 = set_TXTValue(record['ResourceRecords'][3]['Value'].replace('"', ''))
            value5 = set_TXTValue(record['ResourceRecords'][4]['Value'].replace('"', ''))
            value6 = set_TXTValue(record['ResourceRecords'][5]['Value'].replace('"', ''))

            render_TXT_records("TXT6", zoneName, recordName, 1, resource,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6)

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 6_TXT \n")

        elif (len(record['ResourceRecords'])) == 7:
            value1 = set_TXTValue(record['ResourceRecords'][0]['Value'].replace('"', ''))
            value2 = set_TXTValue(record['ResourceRecords'][1]['Value'].replace('"', ''))
            value3 = set_TXTValue(record['ResourceRecords'][2]['Value'].replace('"', ''))
            value4 = set_TXTValue(record['ResourceRecords'][3]['Value'].replace('"', ''))
            value5 = set_TXTValue(record['ResourceRecords'][4]['Value'].replace('"', ''))
            value6 = set_TXTValue(record['ResourceRecords'][5]['Value'].replace('"', ''))
            value7 = set_TXTValue(record['ResourceRecords'][6]['Value'].replace('"', ''))

            render_TXT_records("TXT7", zoneName, recordName, 1, resource,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7)

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 7_TXT \n")

        elif (len(record['ResourceRecords'])) == 8:
            value1 = set_TXTValue(record['ResourceRecords'][0]['Value'].replace('"', ''))
            value2 = set_TXTValue(record['ResourceRecords'][1]['Value'].replace('"', ''))
            value3 = set_TXTValue(record['ResourceRecords'][2]['Value'].replace('"', ''))
            value4 = set_TXTValue(record['ResourceRecords'][3]['Value'].replace('"', ''))
            value5 = set_TXTValue(record['ResourceRecords'][4]['Value'].replace('"', ''))
            value6 = set_TXTValue(record['ResourceRecords'][5]['Value'].replace('"', ''))
            value7 = set_TXTValue(record['ResourceRecords'][6]['Value'].replace('"', ''))
            value8 = set_TXTValue(record['ResourceRecords'][7]['Value'].replace('"', ''))

            render_TXT_records("TXT8", zoneName, recordName, 1, resource,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, value8=value8)

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 8_TXT \n")

        elif (len(record['ResourceRecords'])) == 9:
            value1 = set_TXTValue(record['ResourceRecords'][0]['Value'].replace('"', ''))
            value2 = set_TXTValue(record['ResourceRecords'][1]['Value'].replace('"', ''))
            value3 = set_TXTValue(record['ResourceRecords'][2]['Value'].replace('"', ''))
            value4 = set_TXTValue(record['ResourceRecords'][3]['Value'].replace('"', ''))
            value5 = set_TXTValue(record['ResourceRecords'][4]['Value'].replace('"', ''))
            value6 = set_TXTValue(record['ResourceRecords'][5]['Value'].replace('"', ''))
            value7 = set_TXTValue(record['ResourceRecords'][6]['Value'].replace('"', ''))
            value8 = set_TXTValue(record['ResourceRecords'][7]['Value'].replace('"', ''))
            value9 = set_TXTValue(record['ResourceRecords'][8]['Value'].replace('"', ''))
            
            render_TXT_records("TXT9", zoneName, recordName, 1, resource,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, value8=value8, value9=value9)

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 9_TXT \n")
                
        elif (len(record['ResourceRecords'])) == 10:
            value1 = set_TXTValue(record['ResourceRecords'][0]['Value'].replace('"', ''))
            value2 = set_TXTValue(record['ResourceRecords'][1]['Value'].replace('"', ''))
            value3 = set_TXTValue(record['ResourceRecords'][2]['Value'].replace('"', ''))
            value4 = set_TXTValue(record['ResourceRecords'][3]['Value'].replace('"', ''))
            value5 = set_TXTValue(record['ResourceRecords'][4]['Value'].replace('"', ''))
            value6 = set_TXTValue(record['ResourceRecords'][5]['Value'].replace('"', ''))
            value7 = set_TXTValue(record['ResourceRecords'][6]['Value'].replace('"', ''))
            value8 = set_TXTValue(record['ResourceRecords'][7]['Value'].replace('"', ''))
            value9 = set_TXTValue(record['ResourceRecords'][8]['Value'].replace('"', ''))
            value10 = record['ResourceRecords'][9]['Value'].replace('"', '')

            render_TXT_records("TXT10", zoneName, recordName, 1, resource,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, value8=value8, value9=value9, 
                value10=value10)

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 10_TXT \n")

        elif (len(record['ResourceRecords'])) > 10:
            value1 = set_TXTValue(record['ResourceRecords'][0]['Value'].replace('"', ''))
            value2 = set_TXTValue(record['ResourceRecords'][1]['Value'].replace('"', ''))
            value3 = set_TXTValue(record['ResourceRecords'][2]['Value'].replace('"', ''))
            value4 = set_TXTValue(record['ResourceRecords'][3]['Value'].replace('"', ''))
            value5 = set_TXTValue(record['ResourceRecords'][4]['Value'].replace('"', ''))
            value6 = set_TXTValue(record['ResourceRecords'][5]['Value'].replace('"', ''))
            value7 = set_TXTValue(record['ResourceRecords'][6]['Value'].replace('"', ''))
            value8 = set_TXTValue(record['ResourceRecords'][7]['Value'].replace('"', ''))
            value9 = set_TXTValue(record['ResourceRecords'][8]['Value'].replace('"', ''))
            
            render_TXT_records("TXT10", zoneName, recordName, 1, resource,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, value8=value8, value9=value9, 
                value10="##TODO_MORE_THAN_10_VALUES")

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 10+_TXT \n")

        return True
    return False

# addes resources to resources['NS'] 
def ns(zoneName, record):
    # match = re.match(NS, record)
    print(record)
    match = (record['Type'] == 'NS')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        resources['NS'][resource] = { 'name': recordName }  
      # check the number of values in the ns record
        x = int(len(record['ResourceRecords']))
        if x == 1:
            resources['NS'][resource] = {'name': recordName}
            
            render_NS_records("NS", zoneName, recordName, 1, resource,
                value1=removeDotFromEnd(record['ResourceRecords'][0]['Value']))

        elif x == 2:           
            resources['NS'][resource] = {'name': recordName}

            render_NS_records("NS2", zoneName, recordName, 1, resource,
                value1=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                value2=removeDotFromEnd(record['ResourceRecords'][1]['Value']))
        
        elif x == 3:           
            resources['NS'][resource] = {'name': recordName}

            render_NS_records("NS3", zoneName, recordName, 1, resource,
                value1=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                value2=removeDotFromEnd(record['ResourceRecords'][1]['Value']), 
                value3=removeDotFromEnd(record['ResourceRecords'][2]['Value']))

        elif x == 4:           
            resources['NS'][resource] = {'name': recordName}

            render_NS_records("NS3", zoneName, recordName, 1, resource,
                value1=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                value2=removeDotFromEnd(record['ResourceRecords'][1]['Value']), 
                value3=removeDotFromEnd(record['ResourceRecords'][2]['Value']),
                value4=removeDotFromEnd(record['ResourceRecords'][3]['Value']))
                 
        return True
    return False

# addes resources to resources['SPF'] 
def spf(zoneName, record):
    # match = re.match(A, record)
    print(record)
    match = (record['Type'] == 'SPF')
    if match:
        
        value = record['ResourceRecords'][0]['Value'].replace('"', '')
        if re.match(r'.*DKIM', value):
            value = '; '.join(re.sub(pattern=r'\s+|\\;', repl='', string=value).split(';')).strip()
        
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        resources['SPF'][resource] = { 'name': recordName }  

        render_single_value_records("SPF", zoneName, recordName, 1, value, resource)

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
        if a(set_ZoneName(zone), record):
            continue
        if aaaa(set_ZoneName(zone), record):
            continue
        if cname(set_ZoneName(zone), record):
            continue
        if mx(set_ZoneName(zone), record):
            continue
        if txt(set_ZoneName(zone), record):
            continue
        if spf(set_ZoneName(zone), record):
            continue
        # exclude NS records of the parent zone
        if record['Name'] != zone['Name'] and ns(set_ZoneName(zone), record):
            continue
        print(record)

# render for all files
def render(zone, rs, zoneName, account_id, cloudflare_ns_record):
    env = jinja2.Environment(loader=jinja2.PackageLoader('terraform_named_cloudflare', 'templates'))

    # main.tf
    template = env.get_template('main.tf.j2')
    with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/main.tf', 'w') as target:
        target.write(template.render(account_id=account_id, zoneName=zoneName))

    # Zone.tf
    # cloudflare_zone_name=zoneName - replacing the _ with .
    template = env.get_template('Zone.tf.j2')
    with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/zone.tf', 'w') as target:
        target.write(template.render(terrafromResource=zoneName, cloudflare_zone_name=zoneName.replace('_', '.')))

    # countRecords.txt
    recordA         = len(resources['A'])
    recordAAAA      = len(resources['AAAA'])
    recordCANME     = len(resources['CNAME'])
    recordMX        = len(resources['MX'])
    recordSRV       = len(resources['SRV'])
    recordTXT       = len(resources['TXT'])
    recordNS        = len(resources['NS'])
    recordSPF       = len(resources['SPF'])
    recordsCreated  = recordA + recordAAAA + recordCANME + recordMX + recordSRV + recordTXT + recordNS + recordSPF
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
        # create file only for the necessary records
        if not len(resources[item]) == 0:
            env = jinja2.Environment(loader=jinja2.PackageLoader('terraform_named_cloudflare', 'templates'))
            template = env.get_template(f'nslookup{item}.sh.j2')
            with open(f"./{AWS_ACCOUNTID}/{zoneName}/validateRecords/nslookup{item}.sh", 'a') as target:
                target.write(template.render(resources=resources[item], parentDomain=zoneName.replace('_', '.'), 
                cloudflare_ns_record=cloudflare_ns_record, space=" "))

            # Read in the file
            with open(f"./{AWS_ACCOUNTID}/{zoneName}/validateRecords/nslookup{item}.sh", 'r') as file :
                filedata = file.read()

            # Replace the target string
            # replace duplicate parent domain name in nslookup file
            # for example: facebook.com.facebook.com -> facebook.com
            filedata = filedata.replace(f"{zone['Name'][0:-1]}.{zone['Name'][0:-1]}", f"{zone['Name'][0:-1]}")

            # Write the file out again
            with open(f"./{AWS_ACCOUNTID}/{zoneName}/validateRecords/nslookup{item}.sh", 'w') as file:
                file.write(filedata)

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

            # set zone name for folder name and resource name
            zoneName = set_ZoneName(zone)
            # check if folder exists
            if os.path.exists("./"+AWS_ACCOUNTID+"/"+zoneName):
                pass
            else:
                os.mkdir("./"+AWS_ACCOUNTID+"/"+zoneName)

            # check if folder exists
            if os.path.exists("./"+AWS_ACCOUNTID+"/"+zoneName+"/validateRecords"):
                pass
            else:
                os.mkdir("./"+AWS_ACCOUNTID+"/"+zoneName+"/validateRecords")
            
            # parsing through the records list and write records to 'record_type.tf'
            parse_zone(zone, rs)

            # validation files, zone file, main file
            render(zone, rs, zoneName, account_id, cloudflare_ns_record)

            # terraform fmt check
            os.system('cd ./'+AWS_ACCOUNTID+'/'+zoneName+' && terraform fmt && cd -')

            # change premissions:
            os.system('cd ./'+AWS_ACCOUNTID+'/'+zoneName+'/validateRecords && chmod +x *.sh && cd -')

            # empty resources dict for new zone
            for i in resources:
                resources[i].clear()
                
        # if it's a private zone - write the filtered zone name to file
        else:
            zoneName = set_ZoneName(zone)
            with open("./"+AWS_ACCOUNTID+'/'+AWS_ACCOUNTID+'_PrivateZoneFiltered.txt', 'a') as target:
                target.write(zoneName.replace('_', '.') + "\n")


if __name__ == '__main__':
    main()
