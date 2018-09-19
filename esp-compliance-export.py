from __future__ import print_function
import esp_api_lib
import argparse
from fnmatch import fnmatch


def compliance_standards_filter(compliance_standards_list, custom_compliance_standards_list, standard_name_search):
    # Determine the standard(s) desired for export
    standards_id_list = []
    custom_standards_id_list = []
    for compliance_standard in compliance_standards_list:
        if fnmatch(compliance_standard['attributes']['name'].encode('utf-8').lower(), standard_name_search.lower()):
            standards_id_list.append(int(compliance_standard['id']))
            print(compliance_standard['attributes']['name'].encode('utf-8'))
    for compliance_standard in custom_compliance_standards_list:
        if fnmatch(compliance_standard['attributes']['name'].encode('utf-8').lower(), standard_name_search.lower()):
            custom_standards_id_list.append(int(compliance_standard['id']))
            print(compliance_standard['attributes']['name'].encode('utf-8'))
    return standards_id_list, custom_standards_id_list


def get_compliance_controls(standards_id_list, compliance_standards_list, compliance_domains_list, compliance_controls_list, esp_public, esp_secret):
    # Build a new list with the correct formatting
    object_list_new = []

    # Deal with standard compliance frameworks
    for compliance_control in compliance_controls_list:
        object_new = {}
        # Check to see if the control is in a standard being exported
        object_new['compliance_standard_id'] = esp_api_lib.get_id_from_link(compliance_control['relationships']['compliance_standard']['links']['related'])
        if object_new['compliance_standard_id'] in standards_id_list:
            # Get compliance control information
            object_new['compliance_control_id'] = int(compliance_control['id'])
            object_new['compliance_control_description'] = compliance_control['attributes']['description'].encode('utf-8')
            object_new['compliance_control_identifier'] = compliance_control['attributes']['identifier'].encode('utf-8')
            object_new['compliance_control_created_at'] = compliance_control['attributes']['created_at'].encode('utf-8')
            object_new['compliance_control_updated_at'] = compliance_control['attributes']['updated_at'].encode('utf-8')
            object_new['compliance_control_name'] = compliance_control['attributes']['name'].encode('utf-8')
            object_new['compliance_domain_id'] = esp_api_lib.get_id_from_link(compliance_control['relationships']['compliance_domain']['links']['related'])
            object_new['compliance_standard_id'] = esp_api_lib.get_id_from_link(compliance_control['relationships']['compliance_standard']['links']['related'])

            for compliance_domain in compliance_domains_list:
                # Match and get Domain information
                if int(compliance_domain['id']) == object_new['compliance_domain_id']:
                    object_new['compliance_domain_created_at'] = compliance_domain['attributes']['created_at'].encode('utf-8')
                    object_new['compliance_domain_updated_at'] = compliance_domain['attributes']['updated_at'].encode('utf-8')
                    object_new['compliance_domain_name'] = compliance_domain['attributes']['name'].encode('utf-8')
                    object_new['compliance_domain_identifier'] = compliance_domain['attributes']['identifier'].encode('utf-8')
                    break

            for compliance_standard in compliance_standards_list:
                # Match and get Standards information
                if int(compliance_standard['id']) == object_new['compliance_standard_id']:
                    object_new['compliance_standard_description'] = compliance_standard['attributes']['description'].encode('utf-8')
                    object_new['compliance_standard_created_at'] = compliance_standard['attributes']['created_at'].encode('utf-8')
                    object_new['compliance_standard_updated_at'] = compliance_standard['attributes']['updated_at'].encode('utf-8')
                    object_new['compliance_standard_name'] = compliance_standard['attributes']['name'].encode('utf-8')
                    break

            compliance_control_signature_api = 'compliance_controls/' + str(object_new['compliance_control_id']) + '/signatures'
            compliance_control_signature_list = esp_api_lib.object_list_get(compliance_control_signature_api, esp_public, esp_secret)

            for compliance_control_signature in compliance_control_signature_list:
                object_new_with_sig = object_new.copy()
                object_new_with_sig['signature_id'] = int(compliance_control_signature['id'])
                object_new_with_sig['signature_description'] = compliance_control_signature['attributes']['description'].encode('utf-8')
                object_new_with_sig['signature_identifier'] = compliance_control_signature['attributes']['identifier'].encode('utf-8')
                object_new_with_sig['signature_created_at'] = compliance_control_signature['attributes']['created_at'].encode('utf-8')
                object_new_with_sig['signature_updated_at'] = compliance_control_signature['attributes']['updated_at'].encode('utf-8')
                object_new_with_sig['signature_name'] = compliance_control_signature['attributes']['name'].encode('utf-8')
                object_new_with_sig['signature_resolution'] = compliance_control_signature['attributes']['resolution'].encode('utf-8')
                object_new_with_sig['signature_risk_level'] = compliance_control_signature['attributes']['risk_level'].encode('utf-8')
                object_new_with_sig['signature_service_id'] = esp_api_lib.get_id_from_link(compliance_control_signature['relationships']['service']['links']['related'])
                object_new_with_sig['signature_custom'] = False

                object_list_new.append(object_new_with_sig)

            #object_list_new.append(object_new)  # Only used if SIG block is commented out
    return object_list_new


def get_custom_compliance_controls(custom_standards_id_list, custom_compliance_standards_list, custom_compliance_domains_list, custom_compliance_controls_list, esp_public, esp_secret):
    # Build a new list with the correct formatting
    object_list_new = []

    # Deal with standard compliance frameworks
    for compliance_control in custom_compliance_controls_list:
        object_new = {}
        # Check to see if the control is in a standard being exported
        object_new['compliance_standard_id'] = esp_api_lib.get_id_from_link(compliance_control['relationships']['custom_compliance_standard']['links']['related'])
        if object_new['compliance_standard_id'] in custom_standards_id_list:
            object_new['compliance_control_id'] = int(compliance_control['id'])
            object_new['compliance_control_description'] = compliance_control['attributes']['description'].encode('utf-8')
            object_new['compliance_control_identifier'] = compliance_control['attributes']['identifier'].encode('utf-8')
            object_new['compliance_control_created_at'] = compliance_control['attributes']['created_at'].encode('utf-8')
            object_new['compliance_control_updated_at'] = compliance_control['attributes']['updated_at'].encode('utf-8')
            object_new['compliance_control_name'] = compliance_control['attributes']['name'].encode('utf-8')
            object_new['compliance_domain_id'] = esp_api_lib.get_id_from_link(compliance_control['relationships']['custom_compliance_domain']['links']['related'])

            for compliance_domain in custom_compliance_domains_list:
                if int(compliance_domain['id']) == object_new['compliance_domain_id']:
                    object_new['compliance_domain_created_at'] = compliance_domain['attributes']['created_at'].encode('utf-8')
                    object_new['compliance_domain_updated_at'] = compliance_domain['attributes']['updated_at'].encode('utf-8')
                    object_new['compliance_domain_name'] = compliance_domain['attributes']['name'].encode('utf-8')
                    object_new['compliance_domain_identifier'] = compliance_domain['attributes']['identifier'].encode('utf-8')
                    break

            for compliance_standard in custom_compliance_standards_list:
                if int(compliance_standard['id']) == object_new['compliance_standard_id']:
                    object_new['compliance_standard_description'] = compliance_standard['attributes']['description'].encode('utf-8')
                    object_new['compliance_standard_created_at'] = compliance_standard['attributes']['created_at'].encode('utf-8')
                    object_new['compliance_standard_updated_at'] = compliance_standard['attributes']['updated_at'].encode('utf-8')
                    object_new['compliance_standard_name'] = compliance_standard['attributes']['name'].encode('utf-8')
                    break

            # Get attached signatures from link and add each as a line item
            compliance_control_signature_api = 'custom_compliance_controls/' + str(object_new['compliance_control_id']) + '/signatures'
            compliance_control_signature_list = esp_api_lib.object_list_get(compliance_control_signature_api, esp_public, esp_secret)

            for compliance_control_signature_link in compliance_control_signature_list:
                object_new_with_sig = object_new.copy()
                object_new_with_sig['signature_id'] = esp_api_lib.get_id_from_link(compliance_control_signature_link['relationships']['signature']['links']['related'])

                compliance_control_signature_api_single = 'signatures/%d' % object_new_with_sig['signature_id']
                compliance_control_signature = esp_api_lib.object_get(compliance_control_signature_api_single, esp_public, esp_secret)

                object_new_with_sig['signature_description'] = compliance_control_signature['attributes']['description'].encode('utf-8')
                object_new_with_sig['signature_identifier'] = compliance_control_signature['attributes']['identifier'].encode('utf-8')
                object_new_with_sig['signature_created_at'] = compliance_control_signature['attributes']['created_at'].encode('utf-8')
                object_new_with_sig['signature_updated_at'] = compliance_control_signature['attributes']['updated_at'].encode('utf-8')
                object_new_with_sig['signature_name'] = compliance_control_signature['attributes']['name'].encode('utf-8')
                object_new_with_sig['signature_resolution'] = compliance_control_signature['attributes']['resolution'].encode('utf-8')
                object_new_with_sig['signature_risk_level'] = compliance_control_signature['attributes']['risk_level'].encode('utf-8')
                object_new_with_sig['signature_service_id'] = esp_api_lib.get_id_from_link(compliance_control_signature['relationships']['service']['links']['related'])
                object_new_with_sig['signature_custom'] = False

                object_list_new.append(object_new_with_sig)

            # Get attached custom signatures from link and add each as a line item
            compliance_control_custom_signature_api = 'custom_compliance_controls/' + str(object_new['compliance_control_id']) + '/custom_signatures'
            compliance_control_custom_signature_list = esp_api_lib.object_list_get(compliance_control_custom_signature_api, esp_public, esp_secret)

            for compliance_control_signature_link in compliance_control_custom_signature_list:
                object_new_with_sig = object_new.copy()
                object_new_with_sig['signature_id'] = esp_api_lib.get_id_from_link(compliance_control_signature_link['relationships']['custom_signature']['links']['related'])

                compliance_control_signature_api_single = 'custom_signatures/%d' % object_new_with_sig['signature_id']
                compliance_control_signature = esp_api_lib.object_get(compliance_control_signature_api_single, esp_public, esp_secret)

                object_new_with_sig['signature_description'] = compliance_control_signature['attributes']['description'].encode('utf-8')
                object_new_with_sig['signature_identifier'] = compliance_control_signature['attributes']['identifier'].encode('utf-8')
                object_new_with_sig['signature_created_at'] = compliance_control_signature['attributes']['created_at'].encode('utf-8')
                object_new_with_sig['signature_updated_at'] = compliance_control_signature['attributes']['updated_at'].encode('utf-8')
                object_new_with_sig['signature_name'] = compliance_control_signature['attributes']['name'].encode('utf-8')
                object_new_with_sig['signature_resolution'] = compliance_control_signature['attributes']['resolution'].encode('utf-8')
                object_new_with_sig['signature_risk_level'] = compliance_control_signature['attributes']['risk_level'].encode('utf-8')
                object_new_with_sig['signature_service_id'] = ''
                object_new_with_sig['signature_custom'] = True

                object_list_new.append(object_new_with_sig)
    return object_list_new


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
        '-complete',
        action='store_true',
        help='(Optional) - Return all of the fields for the objects (not just the template required fields).')

    parser.add_argument(
        '-blank',
        action='store_true',
        help='(Optional) - Exports a blank import template with just the field headers and nothing else.')

    parser.add_argument(
        'export_file_name',
        type=str,
        help='File to export to.')

    parser.add_argument(
        'compliance_standard_name',
        type=str,
        help='Compliance Standard Name(s) to export.  Supports the wildcard use of * and ?')

    args = parser.parse_args()
    # --End parse command line arguments-- #

    # Check to see if they just want a blank template
    compliance_list_new = []
    if args.blank:
        print('Creating a blank template...')
        field_names = ['compliance_standard_name', 'compliance_standard_description', 'compliance_domain_name', 'compliance_domain_identifier', 'compliance_control_name',
                       'compliance_control_identifier', 'compliance_control_description', 'signature_identifier', 'signature_name']
        esp_api_lib.write_to_csv(compliance_list_new, args.export_file_name, field_names)
        print('Blank CSV template created!')
    else:
        print()
        print('Sorting out ESP API Key...')
        esp_public, esp_secret = esp_api_lib.settings_get(args.public, args.secret)

        # --Main-- #
        print('Get the compliance standards objects from the ESP API...')
        compliance_standards_list = esp_api_lib.object_list_get('compliance_standards', esp_public, esp_secret)
        custom_compliance_standards_list = esp_api_lib.object_list_get('custom_compliance_standards', esp_public, esp_secret)

        print('Get list of standard IDs needed for export...')
        standards_id_list, custom_standards_id_list = compliance_standards_filter(compliance_standards_list, custom_compliance_standards_list, args.compliance_standard_name)
        if len(standards_id_list) > 0:
            print('Getting the Domains and Controls data from the ESP API (Built-in Compliance)...')
            compliance_domains_list = esp_api_lib.object_list_get('compliance_domains', esp_public, esp_secret)
            compliance_controls_list = esp_api_lib.object_list_get('compliance_controls', esp_public, esp_secret)
            print('Build a new list with the correct formatting and pull the sig lists from the API for line by line export (Built-in Compliance)...')
            compliance_list_new.extend(get_compliance_controls(standards_id_list, compliance_standards_list, compliance_domains_list, compliance_controls_list, esp_public, esp_secret))
            if len(custom_standards_id_list) > 0:
                print('Getting the Domains and Controls data from the ESP API (Custom Compliance)...')
                custom_compliance_domains_list = esp_api_lib.object_list_get('custom_compliance_domains', esp_public, esp_secret)
                custom_compliance_controls_list = esp_api_lib.object_list_get('custom_compliance_controls', esp_public, esp_secret)
                print('Build a new list with the correct formatting and pull the sig lists from the API for line by line export (Custom Compliance - Lots of API calls for this one - may take a while)...')
                compliance_list_new.extend(get_custom_compliance_controls(custom_standards_id_list, custom_compliance_standards_list, custom_compliance_domains_list,
                                                                          custom_compliance_controls_list, esp_public, esp_secret))
        elif len(custom_standards_id_list) > 0:
            print('Getting the Domains and Controls data from the ESP API (Custom Compliance)...')
            custom_compliance_domains_list = esp_api_lib.object_list_get('custom_compliance_domains', esp_public, esp_secret)
            custom_compliance_controls_list = esp_api_lib.object_list_get('custom_compliance_controls', esp_public, esp_secret)
            print('Build a new list with the correct formatting and pull the sig lists from the API for line by line export (Custom Compliance - Lots of API calls for this one - may take a while)...')
            compliance_list_new.extend(get_custom_compliance_controls(custom_standards_id_list, custom_compliance_standards_list, custom_compliance_domains_list,
                                                                      custom_compliance_controls_list, esp_public, esp_secret))
        else:
            esp_api_lib.exit_error(400, 'No Compliance Standards found matching name specified!')

        # Figure out the requested output method
        if args.json:
            print('Export everything out to JSON...')
            esp_api_lib.write_to_json(compliance_list_new, args.export_file_name)
        elif args.complete:
            print('Export everything out to CSV (not import template optimized)...')
            esp_api_lib.write_to_csv(compliance_list_new, args.export_file_name)
        else:
            print('Export everything out to CSV in import template format...')
            field_names = ['compliance_standard_name', 'compliance_standard_description', 'compliance_domain_name', 'compliance_domain_identifier', 'compliance_control_name',
                           'compliance_control_identifier', 'compliance_control_description', 'signature_identifier', 'signature_name']
            esp_api_lib.write_to_csv(compliance_list_new, args.export_file_name, field_names)
        print()
        print('Export complete!')
