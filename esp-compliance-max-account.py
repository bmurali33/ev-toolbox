from __future__ import print_function
import esp_api_lib
import argparse
import json
from fnmatch import fnmatch


def custom_compliance_standards_filter(custom_compliance_standards_list, standard_name_search):
    # Determine the standard(s) desired for export
    custom_standards_id_list = []
    for compliance_standard in custom_compliance_standards_list:
        if fnmatch(compliance_standard['attributes']['name'].encode('utf-8').lower(), standard_name_search.lower()):
            custom_standards_id_list.append(int(compliance_standard['id']))
            print(compliance_standard['attributes']['name'].encode('utf-8'))
    return custom_standards_id_list


# --Execution Block-- #
if __name__ == '__main__':

    # --Parse command line arguments-- #
    parser = argparse.ArgumentParser(prog='esptoolbox')

    parser.add_argument(
        '-p',
        '--public',
        type=str,
        help='ESP API public portion of the key pair')

    parser.add_argument(
        '-s',
        '--secret',
        type=str,
        help='ESP API secret portion of the key pair')

    parser.add_argument(
        '-n',
        '--compliance_standard_name',
        type=str,
        help='**ID or name is required** Compliance Standard Name to update.  Supports the wildcard use of * and ?')

    parser.add_argument(
        '-id',
        '--compliance_standard_id',
        type=int,
        help='**ID or name is required** Custom Compliance Standard ID')

    parser.add_argument(
        '-max',
        '--max_number_of_accounts',
        type=int,
        help='Number of accounts to authorize the custom compliance to be enabled on.')

    args = parser.parse_args()
    # --End parse command line arguments-- #

    print()
    print('Sorting out ESP API Key...')
    esp_public, esp_secret = esp_api_lib.settings_get(args.public, args.secret)

    # --Main-- #
    compliance_standard_id = 0
    if args.compliance_standard_id is None and args.compliance_standard_name is None:
        esp_api_lib.exit_error(400, 'You need to either fill in a Custom Compliance Standard Name or ID.')
    elif args.compliance_standard_id is not None and args.compliance_standard_name is not None:
        esp_api_lib.exit_error(400, 'You need to enter an ID OR a Standard Name, not both.')
    elif args.compliance_standard_id is None:
        print('API - Get the custom compliance standard id from name...')
        custom_compliance_standards_list = esp_api_lib.object_list_get('custom_compliance_standards', esp_public, esp_secret)
        custom_standards_id_list = custom_compliance_standards_filter(custom_compliance_standards_list, args.compliance_standard_name)

        if len(custom_standards_id_list) == 1:
            compliance_standard_id = custom_standards_id_list[0]
        elif len(custom_standards_id_list) > 1:
            esp_api_lib.exit_error(400, 'More than 1 Compliance Standards found matching name specified!  Please limit your filter to a single Compliance Standard.')
        else:
            esp_api_lib.exit_error(400, 'No Compliance Standards found matching name specified!')
    else:
        compliance_standard_id = args.compliance_standard_id

    if args.max_number_of_accounts is None:
        print("No new max account number detected.  Pulling existing Custom Compliance Standard Information...")
        print("API - Getting Custom Compliance Standard information...")
        custom_compliance_standard_url = 'custom_compliance_standards/%d' % compliance_standard_id
        custom_compliance_standard_get_response = esp_api_lib.object_get(custom_compliance_standard_url, esp_public, esp_secret)
        print("Full Custom Standard data package:")
        print(json.dumps(custom_compliance_standard_get_response))
        print()
        print("For the standard of ID:")
        print(json.dumps(custom_compliance_standard_get_response['id']))
        print("The current number of allowed accounts is set to:")
        print(json.dumps(custom_compliance_standard_get_response['attributes']['max_accounts']))
    else:
        data = json.dumps({'data': {'attributes': {'max_accounts': args.max_number_of_accounts}}})
        print('API - Setting the Custom Compliance account max...')
        custom_compliance_standard_url = 'custom_compliance_standards/%d' % compliance_standard_id
        custom_compliance_standard_update_response = esp_api_lib.object_patch(custom_compliance_standard_url, data, esp_public, esp_secret)
        if custom_compliance_standard_update_response['attributes']['max_accounts'] == args.max_number_of_accounts:
            print("Update Successful!")
            print(json.dumps(custom_compliance_standard_update_response))
        else:
            print("Update Failed!")
            print(json.dumps(custom_compliance_standard_update_response))
