#!/usr/bin/env python3

import argparse
from threading import activeCount
import jinja2
import re
import boto3
import os
import stat

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
        '-gd',
        '--gd_file',
        help='godaddy csv file',
        default=str(),
        required=True,
        type=str
    )
    return parser



def render_gd_zones(zoneName, gd_folder_name, cf_account_id):
    env = jinja2.Environment(loader=jinja2.PackageLoader('terraform_named_cloudflare', 'templates'))

    # main.tf
    template = env.get_template('main.tf.j2')
    with open("./" + gd_folder_name + "/" +zoneName + '/main.tf', 'w') as target:
        target.write(template.render(account_id=cf_account_id, zoneName=zoneName))

    # cloudflareZone.tf
    # cloudflare_zone_name=zoneName - replacing the _ with .
    template = env.get_template('cloudflareZone.tf.j2')
    with open("./" + gd_folder_name + "/" + zoneName + '/zone.tf', 'w') as target:
        target.write(template.render(terrafromResource=zoneName, cloudflare_zone_name = zoneName.replace('_', '.')))

    # create git.sh file
    template = env.get_template('git.sh.j2')
    with open("./" + gd_folder_name + "/" + zoneName + '/gitcmd.sh', 'w') as target:
        target.write(template.render(terrafromResource=zoneName, cloudflare_zone_name = zoneName.replace('_', '.')))
        st = os.stat("./" + gd_folder_name + "/" + zoneName + '/gitcmd.sh')
        os.chmod("./" + gd_folder_name + "/" + zoneName + '/gitcmd.sh', st.st_mode | stat.S_IEXEC)



def main():
    # get input parameters
    args = parse_arguments().parse_args()
    account_id = args.account_id
    gd_file_name = args.gd_file
    
    gd_folder_name = gd_file_name.replace('.csv', '')

    # Using readlines()
    file1 = open(gd_file_name, 'r')
    Lines = file1.readlines()

    # check if folder exists
    if os.path.exists("./" + gd_folder_name):
        pass
    else:
        os.mkdir("./" + gd_folder_name)
    
    # filter out private domains
    for zone in Lines:

        # set zone name
        zoneName = zone.split(',')[0].replace('.', '_').lower()

        # check if folder exists
        if os.path.exists("./" + gd_folder_name + "/" + zoneName):
            pass
        else:
            os.mkdir("./" + gd_folder_name + "/" + zoneName)

        # check if folder exists
        # if os.path.exists("./" + gd_folder_name + "/" + zoneName + "/error"):
        #     pass
        # else:
        #     os.mkdir("./" + gd_folder_name + "/" + zoneName + "/error")

        render_gd_zones(zoneName, gd_folder_name, account_id)
          



if __name__ == '__main__':
    main()
