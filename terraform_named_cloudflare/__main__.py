#!/usr/bin/env python3

import argparse
from threading import activeCount
import jinja2
import re
import boto3
import os
import subprocess

globals
AWS_ACCOUNTID="1111"
ENV = jinja2.Environment(loader=jinja2.PackageLoader('terraform_named_cloudflare', 'templates'))

# used to count records that were created
resources = {
    'A': {},
    'AAAA': {},
    'CNAME': {},
    'MX': {},
    'SRV': {},
    'SPF': {},
    'TXT': {},
    'NS': {}
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

# addes resources to resources['A'] 
def a(zoneName, record):
    # match = re.match(A, record)
    print(record)
    match = (record['Type'] == 'A')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        if 'ResourceRecords' in record:
            resources['A'][resource] = { 'name': recordName }
            template = ENV.get_template('A.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/A.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                terrafromResource=resource, zone_id=zoneName))
        elif 'AliasTarget' in record:
            resources['CNAME'][resource] = { 'name': recordName }
            template = ENV.get_template('CNAME.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/CNAME.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value=removeDotFromEnd(record['AliasTarget']['DNSName']), 
                terrafromResource=resource, zone_id=zoneName))   
        return True
    return False

# addes resources to resources['AAAA'] 
def aaaa(zoneName, record):
    match = (record['Type'] == 'AAAA')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        if 'ResourceRecords' in  record:
            resources['AAAA'][resource] = { 'name': recordName }
            ##TODO create function for writing records                  
            template = ENV.get_template('AAAA.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/AAAA.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                terrafromResource=resource, zone_id=zoneName))
        elif 'AliasTarget' in record:
            resources['CNAME'][resource] = { 'name': recordName }
            template = ENV.get_template('CNAME.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/CNAME.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value=removeDotFromEnd(record['AliasTarget']['DNSName']), 
                terrafromResource=resource, zone_id=zoneName)) 
        return True
    return False

# addes resources to resources['CNAME'] 
def cname(zoneName, record):
    # match = re.match(CNAME, record)
    match = (record['Type'] == 'CNAME')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        resources['CNAME'][resource] = { 'name': recordName }  
        if 'ResourceRecords' in  record:   
            template = ENV.get_template('CNAME.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/CNAME.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                terrafromResource=resource, zone_id=zoneName))
        elif 'AliasTarget' in record:
            template = ENV.get_template('CNAME.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/CNAME.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value=removeDotFromEnd(record['AliasTarget']['DNSName']), 
                terrafromResource=resource, zone_id=zoneName))  
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

            template = ENV.get_template('MX.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/MX.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=removeDotFromEnd(setPV[1]), priority1=setPV[0], 
                terrafromResource=resource, zone_id=zoneName)) 

        elif x == 2:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()  

            template = ENV.get_template('MX2.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/MX.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=removeDotFromEnd(setPV[1]), priority1=setPV[0], 
                value2=removeDotFromEnd(setPV2[1]), priority2=setPV2[0], 
                terrafromResource=resource, zone_id=zoneName)) 

        elif x == 3:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()
            setPV3 = record['ResourceRecords'][2]['Value'].split() 

            template = ENV.get_template('MX3.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/MX.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=removeDotFromEnd(setPV[1]), priority1=setPV[0], 
                value2=removeDotFromEnd(setPV2[1]), priority2=setPV2[0], 
                value3=removeDotFromEnd(setPV3[1]), priority3= setPV3[0],
                terrafromResource=resource, zone_id=zoneName))

        elif x == 4:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()
            setPV3 = record['ResourceRecords'][2]['Value'].split()
            setPV4 = record['ResourceRecords'][3]['Value'].split()

            template = ENV.get_template('MX4.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/MX.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=removeDotFromEnd(setPV[1]), priority1=setPV[0], 
                value2=removeDotFromEnd(setPV2[1]), priority2=setPV2[0], 
                value3=removeDotFromEnd(setPV3[1]), priority3= setPV3[0], 
                value4=removeDotFromEnd(setPV4[1]), priority4=setPV4[0], 
                terrafromResource=resource, zone_id=zoneName))

        elif x == 5:
            # get priority and value
            setPV = record['ResourceRecords'][0]['Value'].split()
            setPV2 = record['ResourceRecords'][1]['Value'].split()
            setPV3 = record['ResourceRecords'][2]['Value'].split()
            setPV4 = record['ResourceRecords'][3]['Value'].split()
            setPV5 = record['ResourceRecords'][4]['Value'].split()

            template = ENV.get_template('MX5.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/MX.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=removeDotFromEnd(setPV[1]), priority1=setPV[0], 
                value2=removeDotFromEnd(setPV2[1]), priority2=setPV2[0], 
                value3=removeDotFromEnd(setPV3[1]), priority3= setPV3[0], 
                value4=removeDotFromEnd(setPV4[1]), priority4=setPV4[0], 
                value5= removeDotFromEnd(setPV5[1]), priority5=setPV5[0], 
                terrafromResource=resource, zone_id=zoneName))
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

        value = record['ResourceRecords'][0]['Value'].replace('"', '')
        if re.match(r'.*DKIM', value):
            value = '; '.join(re.sub(pattern=r'\s+|\\;', repl='', string=value).split(';')).strip()

        # Silently ignore TXT records with empty string values as not supported by CloudFlare
        if not value:
            return True
        if (len(record['ResourceRecords'])) == 1:
            value1 = record['ResourceRecords'][0]['Value'].replace('"', '')

            template = ENV.get_template('TXT.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/TXT.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, value1=value1, 
                terrafromResource=resource, zone_id=zoneName)) 

        elif (len(record['ResourceRecords'])) == 2:
            value1 = record['ResourceRecords'][0]['Value'].replace('"', '')
            value2 = record['ResourceRecords'][1]['Value'].replace('"', '')

            template = ENV.get_template('TXT2.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/TXT.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=value1, value2=value2, 
                terrafromResource=resource, zone_id=zoneName)) 

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 2_TXT \n")

        elif (len(record['ResourceRecords'])) == 3:
            value1 = record['ResourceRecords'][0]['Value'].replace('"', '')
            value2 = record['ResourceRecords'][1]['Value'].replace('"', '')
            value3 = record['ResourceRecords'][2]['Value'].replace('"', '')

            template = ENV.get_template('TXT3.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/TXT.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=value1, value2=value2, value3=value3, 
                terrafromResource=resource, zone_id=zoneName))

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 3_TXT \n")

        elif (len(record['ResourceRecords'])) == 4:
            value1 = record['ResourceRecords'][0]['Value'].replace('"', '')
            value2 = record['ResourceRecords'][1]['Value'].replace('"', '')
            value3 = record['ResourceRecords'][2]['Value'].replace('"', '')
            value4 = record['ResourceRecords'][3]['Value'].replace('"', '')

            template = ENV.get_template('TXT4.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/TXT.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=value1, value2=value2, value3=value3, 
                value4=value4, terrafromResource=resource, 
                zone_id=zoneName))

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 4_TXT \n")

        elif (len(record['ResourceRecords'])) == 5:
            value1 = record['ResourceRecords'][0]['Value'].replace('"', '')
            value2 = record['ResourceRecords'][1]['Value'].replace('"', '')
            value3 = record['ResourceRecords'][2]['Value'].replace('"', '')
            value4 = record['ResourceRecords'][3]['Value'].replace('"', '')
            value5 = record['ResourceRecords'][4]['Value'].replace('"', '')

            template = ENV.get_template('TXT5.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/TXT.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, terrafromResource=resource, 
                zone_id=zoneName))

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 5_TXT \n")

        elif (len(record['ResourceRecords'])) == 6:
            value1 = record['ResourceRecords'][0]['Value'].replace('"', '')
            value2 = record['ResourceRecords'][1]['Value'].replace('"', '')
            value3 = record['ResourceRecords'][2]['Value'].replace('"', '')
            value4 = record['ResourceRecords'][3]['Value'].replace('"', '')
            value5 = record['ResourceRecords'][4]['Value'].replace('"', '')
            value6 = record['ResourceRecords'][5]['Value'].replace('"', '')

            template = ENV.get_template('TXT6.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/TXT.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                terrafromResource=resource, zone_id=zoneName))

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 6_TXT \n")

        elif (len(record['ResourceRecords'])) == 7:
            value1 = record['ResourceRecords'][0]['Value'].replace('"', '')
            value2 = record['ResourceRecords'][1]['Value'].replace('"', '')
            value3 = record['ResourceRecords'][2]['Value'].replace('"', '')
            value4 = record['ResourceRecords'][3]['Value'].replace('"', '')
            value5 = record['ResourceRecords'][4]['Value'].replace('"', '')
            value6 = record['ResourceRecords'][5]['Value'].replace('"', '')
            value7 = record['ResourceRecords'][6]['Value'].replace('"', '')

            template = ENV.get_template('TXT7.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/TXT.tf', 'a') as target:
                target.write(template.render(name=recordName, 
                ttl=1, value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, terrafromResource=resource, zone_id=zoneName))

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 7_TXT \n")

        elif (len(record['ResourceRecords'])) == 8:
            value1 = record['ResourceRecords'][0]['Value'].replace('"', '')
            value2 = record['ResourceRecords'][1]['Value'].replace('"', '')
            value3 = record['ResourceRecords'][2]['Value'].replace('"', '')
            value4 = record['ResourceRecords'][3]['Value'].replace('"', '')
            value5 = record['ResourceRecords'][4]['Value'].replace('"', '')
            value6 = record['ResourceRecords'][5]['Value'].replace('"', '')
            value7 = record['ResourceRecords'][6]['Value'].replace('"', '')
            value8 = record['ResourceRecords'][7]['Value'].replace('"', '')

            template = ENV.get_template('TXT8.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/TXT.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, value8=value8, 
                terrafromResource=resource, zone_id=zoneName))

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 8_TXT \n")

        elif (len(record['ResourceRecords'])) == 9:
            value1 = record['ResourceRecords'][0]['Value'].replace('"', '')
            value2 = record['ResourceRecords'][1]['Value'].replace('"', '')
            value3 = record['ResourceRecords'][2]['Value'].replace('"', '')
            value4 = record['ResourceRecords'][3]['Value'].replace('"', '')
            value5 = record['ResourceRecords'][4]['Value'].replace('"', '')
            value6 = record['ResourceRecords'][5]['Value'].replace('"', '')
            value7 = record['ResourceRecords'][6]['Value'].replace('"', '')
            value8 = record['ResourceRecords'][7]['Value'].replace('"', '')
            value9 = record['ResourceRecords'][8]['Value'].replace('"', '')

            template = ENV.get_template('TXT9.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/TXT.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, value8=value8, value9=value9, 
                terrafromResource=resource, zone_id=zoneName))

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 9_TXT \n")
                
        elif (len(record['ResourceRecords'])) == 10:
            value1 = record['ResourceRecords'][0]['Value'].replace('"', '')
            value2 = record['ResourceRecords'][1]['Value'].replace('"', '')
            value3 = record['ResourceRecords'][2]['Value'].replace('"', '')
            value4 = record['ResourceRecords'][3]['Value'].replace('"', '')
            value5 = record['ResourceRecords'][4]['Value'].replace('"', '')
            value6 = record['ResourceRecords'][5]['Value'].replace('"', '')
            value7 = record['ResourceRecords'][6]['Value'].replace('"', '')
            value8 = record['ResourceRecords'][7]['Value'].replace('"', '')
            value9 = record['ResourceRecords'][8]['Value'].replace('"', '')
            value10 = record['ResourceRecords'][9]['Value'].replace('"', '')

            template = ENV.get_template('TXT10.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/TXT.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, value8=value8, value9=value9, value10=value10, 
                terrafromResource=resource, zone_id=zoneName))

            with open("./"+AWS_ACCOUNTID+'/TXTcount.txt', 'a') as target:
                target.write(f"{resource} {recordName} 10_TXT \n")

        elif (len(record['ResourceRecords'])) > 10:
            value1 = record['ResourceRecords'][0]['Value'].replace('"', '')
            value2 = record['ResourceRecords'][1]['Value'].replace('"', '')
            value3 = record['ResourceRecords'][2]['Value'].replace('"', '')
            value4 = record['ResourceRecords'][3]['Value'].replace('"', '')
            value5 = record['ResourceRecords'][4]['Value'].replace('"', '')
            value6 = record['ResourceRecords'][5]['Value'].replace('"', '')
            value7 = record['ResourceRecords'][6]['Value'].replace('"', '')
            value8 = record['ResourceRecords'][7]['Value'].replace('"', '')
            value9 = record['ResourceRecords'][8]['Value'].replace('"', '')

            template = ENV.get_template('TXT10.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/TXT.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, value8=value8, value9=value9, 
                value10="##TODO_MORE_THAN_10_VALUES", 
                terrafromResource=resource, zone_id=zoneName))

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

            template = ENV.get_template('NS.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/NS.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                terrafromResource=resource, zone_id=zoneName)) 

        elif x == 2:           
            resources['NS'][resource] = {'name': recordName}

            template = ENV.get_template('NS2.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/NS.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                value2=removeDotFromEnd(record['ResourceRecords'][1]['Value']), 
                terrafromResource=resource, zone_id=zoneName))
        
        elif x == 3:           
            resources['NS'][resource] = {'name': recordName}

            template = ENV.get_template('NS3.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/NS.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                value2=removeDotFromEnd(record['ResourceRecords'][1]['Value']), 
                value3=removeDotFromEnd(record['ResourceRecords'][2]['Value']),
                terrafromResource=resource, zone_id=zoneName))

        elif x == 4:           
            resources['NS'][resource] = {'name': recordName}

            template = ENV.get_template('NS3.tf.j2')
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/NS.tf', 'a') as target:
                target.write(template.render(name=recordName, ttl=1, 
                value1=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                value2=removeDotFromEnd(record['ResourceRecords'][1]['Value']), 
                value3=removeDotFromEnd(record['ResourceRecords'][2]['Value']),
                value4=removeDotFromEnd(record['ResourceRecords'][3]['Value']), 
                terrafromResource=resource, zone_id=zoneName))
                 
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

        template = ENV.get_template('SPF.tf.j2')
        with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/SPF.tf', 'a') as target:
            target.write(template.render(name=recordName, ttl=1, value=value, 
            terrafromResource=resource, zone_id=zoneName)) 

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
            template = env.get_template('nslookup{}.sh.j2'.format(item))
            with open("./"+AWS_ACCOUNTID+"/"+zoneName+'/validateRecords/nslookup{}.sh'.format(item), 'a') as target:
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
            
            # parsing through the records list
            parse_zone(zone, rs)

            # writing to files
            render(zone, rs, zoneName, account_id, cloudflare_ns_record)

            # terraform fmt check
            os.system('cd ./'+AWS_ACCOUNTID+'/'+zoneName+' && terraform fmt && cd -')

            # change premissions:
            os.system('cd ./'+AWS_ACCOUNTID+'/'+zoneName+'/validateRecords && chmod +x *.sh && cd -')

            # remove double parent name from nslookp files
            ##TODO for loop that goes to each sh file and rewrite the double domain name
            with open("/etc/apt/sources.list", "r") as sources:
                lines = sources.readlines()
            with open("/etc/apt/sources.list", "w") as sources:
                for line in lines:
                    sources.write(re.sub(r'^# deb', 'deb', line))
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
