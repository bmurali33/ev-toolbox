from __future__ import print_function
import esp_api_lib
import csv
import sys
import argparse
import json


def signatures_format(signatures_list, custom):
    signatures_list_new = []
    for signature_old in signatures_list:
        signature_new = {}
        signature_new['id'] = signature_old['id'].encode('utf-8')
        signature_new['risk_level'] = signature_old['attributes']['risk_level'].encode('utf-8')
        signature_new['description'] = signature_old['attributes']['description'].encode('utf-8')
        signature_new['created_at'] = signature_old['attributes']['created_at'].encode('utf-8')
        signature_new['updated_at'] = signature_old['attributes']['updated_at'].encode('utf-8')
        signature_new['identifier'] = signature_old['attributes']['identifier'].encode('utf-8')
        signature_new['resolution'] = signature_old['attributes']['resolution'].encode('utf-8')
        signature_new['name'] = signature_old['attributes']['name'].encode('utf-8')
        signature_new['signature_custom'] = custom
        signatures_list_new.append(signature_new)
    return signatures_list_new


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
        '-json',
        action='store_true',
        help='(Optional) - Return the objects in JSON format.')

    parser.add_argument(
        '-custom',
        action='store_true',
        help='(Optional) - Export only the custom signatures.')

    parser.add_argument(
        '-builtin',
        action='store_true',
        help='(Optional) - Export only the built-in signatures.')

    parser.add_argument(
        'export_file_name',
        type=str,
        help='File to export to.')

    args = parser.parse_args()
    # --End parse command line arguments-- #

    # Sort out ESP API Key
    esp_public, esp_secret = esp_api_lib.settings_get(args.public, args.secret)

    # --Main-- #
    if args.custom and not args.builtin:
        print('Getting the custom signatures from the API...')
        custom_signatures_list = esp_api_lib.object_list_get('custom_signatures', esp_public, esp_secret)
        print('Formatting results into export format...')
        signatures_list_formatted = signatures_format(custom_signatures_list, True)

    elif not args.custom and args.builtin:
        print('Getting the built-in signatures from the API...')
        signatures_list = esp_api_lib.object_list_get('signatures', esp_public, esp_secret)
        print('Formatting results into export format...')
        signatures_list_formatted = signatures_format(signatures_list, False)

    else:
        print('Getting the built-in signatures from the API...')
        signatures_list = esp_api_lib.object_list_get('signatures', esp_public, esp_secret)
        print('Getting the custom signatures from the API...')
        custom_signatures_list = esp_api_lib.object_list_get('custom_signatures', esp_public, esp_secret)
        print('Formatting results into export format...')
        signatures_list_formatted = signatures_format(signatures_list, False)
        signatures_list_formatted.extend(signatures_format(custom_signatures_list, True))

    # Figure out the requested output method
    if args.json:
        print('Exporting results into JSON format...')
        esp_api_lib.write_to_json(signatures_list_formatted, args.export_file_name)
    else:
        print('Exporting results into CSV format...')
        esp_api_lib.write_to_csv(signatures_list_formatted, args.export_file_name)
    print()
    print('Export complete!')
