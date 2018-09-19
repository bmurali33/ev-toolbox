from __future__ import print_function
import esp_api_lib
import argparse
import json


# Get the compliance from the CSV
def compliance_get(csv_list, esp_public, esp_secret):
    # Validate expected fields were imported
    keys = ['compliance_standard_name',
            'compliance_standard_description',
            'compliance_domain_name',
            'compliance_domain_identifier',
            'compliance_control_name',
            'compliance_control_identifier',
            'compliance_control_description',
            'signature_identifier']
    for key in keys:
        if key not in csv_list[0]:
            esp_api_lib.exit_error(400, 'Expected key missing from import CSV: ' + str(key))

    # Validate and set Org ID
    organization_list = esp_api_lib.object_list_get('organizations', esp_public, esp_secret)
    if len(organization_list) != 1:
        esp_api_lib.exit_error(500, 'Expected exactly 1 top level Organization, but got ' + str(len(organization_list)))
    organization_id = int(organization_list[0]['id'])

    # Validate and create nested structures for import
    import_dict = {}
    for row in csv_list:
        # Set and verify the row has all required values
        standard_name = row['compliance_standard_name'].encode('utf-8')
        if standard_name == '':
            esp_api_lib.exit_error(400, "Import sheet is missing compliance_standard_name for : " + json.dumps(row))

        standard_description = row['compliance_standard_description'].encode('utf-8')
        if standard_description == '':
            esp_api_lib.exit_error(400, "Import sheet is missing compliance_standard_description for : " + json.dumps(row))

        domain_name = row['compliance_domain_name'].encode('utf-8')
        if domain_name == '':
            esp_api_lib.exit_error(400, "Import sheet is missing the compliance_domain_name for : " + json.dumps(row))

        domain_identifier = row['compliance_domain_identifier'].encode('utf-8')
        if domain_identifier == '':
            esp_api_lib.exit_error(400, "Import sheet is missing the compliance_domain_identifier for : " + json.dumps(row))

        control_name = row['compliance_control_name'].encode('utf-8')
        if control_name == '':
            esp_api_lib.exit_error(400, "Import sheet is missing the compliance_control_name for : " + json.dumps(row))

        control_identifier = row['compliance_control_identifier'].encode('utf-8')
        if control_identifier == '':
            esp_api_lib.exit_error(400, "Import sheet is missing the compliance_control_identifier for : " + json.dumps(row))

        control_description = row['compliance_control_description'].encode('utf-8')
        if control_description == '':
            esp_api_lib.exit_error(400, "Import sheet is missing the compliance_control_description for : " + json.dumps(row))

        signature_identifier = row['signature_identifier'].encode('utf-8')
        if signature_identifier == '':
            esp_api_lib.exit_error(400, "Import sheet is missing the signature_identifier for : " + json.dumps(row))

        # Build nested structure
        if standard_name not in import_dict:
            import_dict[standard_name] = {}
            import_dict[standard_name]['organization_id'] = organization_id
            import_dict[standard_name]['compliance_standard_description'] = standard_description
            import_dict[standard_name]['domains'] = {}
            import_dict[standard_name]['domains'][domain_name] = {}
            import_dict[standard_name]['domains'][domain_name]['compliance_domain_identifier'] = domain_identifier
            import_dict[standard_name]['domains'][domain_name]['controls'] = {}
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name] = {}
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['compliance_control_identifier'] = control_identifier
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['compliance_control_description'] = control_description
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['signature_identifier_list'] = [signature_identifier]
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['signature_ids'] = []
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['custom_signature_ids'] = []
        elif domain_name not in import_dict[standard_name]['domains']:
            import_dict[standard_name]['domains'][domain_name] = {}
            import_dict[standard_name]['domains'][domain_name]['compliance_domain_identifier'] = domain_identifier
            import_dict[standard_name]['domains'][domain_name]['controls'] = {}
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name] = {}
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['compliance_control_identifier'] = control_identifier
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['compliance_control_description'] = control_description
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['signature_identifier_list'] = [signature_identifier]
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['signature_ids'] = []
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['custom_signature_ids'] = []
        elif control_name not in import_dict[standard_name]['domains'][domain_name]['controls']:
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name] = {}
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['compliance_control_identifier'] = control_identifier
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['compliance_control_description'] = control_description
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['signature_identifier_list'] = [signature_identifier]
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['signature_ids'] = []
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['custom_signature_ids'] = []
        else:
            import_dict[standard_name]['domains'][domain_name]['controls'][control_name]['signature_identifier_list'].append(signature_identifier)
    return import_dict


def compliance_standard_create(organization_id, name, description, esp_public, esp_secret, max_accounts=None):
    compliance_standard_data = {}
    compliance_standard_data['data'] = {}
    compliance_standard_data['data']['attributes'] = {}
    compliance_standard_data['data']['attributes']['organization_id'] = organization_id
    compliance_standard_data['data']['attributes']['name'] = name
    compliance_standard_data['data']['attributes']['description'] = description
    if max_accounts is not None:
        compliance_standard_data['data']['attributes']['max_accounts'] = max_accounts
    compliance_standard_new = esp_api_lib.object_post('custom_compliance_standards', json.dumps(compliance_standard_data), esp_public, esp_secret)
    return compliance_standard_new


def compliance_domain_create(custom_compliance_standard_id, name, identifier, esp_public, esp_secret):
    compliance_domain_data = {}
    compliance_domain_data['data'] = {}
    compliance_domain_data['data']['attributes'] = {}
    compliance_domain_data['data']['attributes']['custom_compliance_standard_id'] = int(custom_compliance_standard_id)
    compliance_domain_data['data']['attributes']['name'] = name.encode('utf-8')
    compliance_domain_data['data']['attributes']['identifier'] = identifier.encode('utf-8')
    compliance_domain_new = esp_api_lib.object_post('custom_compliance_domains', json.dumps(compliance_domain_data), esp_public, esp_secret)
    return compliance_domain_new


def compliance_control_create(custom_compliance_domain_id, name, identifier, description, signature_ids, custom_signature_ids, esp_public, esp_secret):
    compliance_control_data = {}
    compliance_control_data['data'] = {}
    compliance_control_data['data']['attributes'] = {}
    compliance_control_data['data']['attributes']['custom_compliance_domain_id'] = custom_compliance_domain_id
    compliance_control_data['data']['attributes']['name'] = name
    compliance_control_data['data']['attributes']['identifier'] = identifier
    compliance_control_data['data']['attributes']['description'] = description
    compliance_control_data['data']['attributes']['signature_ids'] = signature_ids
    compliance_control_data['data']['attributes']['custom_signature_ids'] = custom_signature_ids
    compliance_control_new = esp_api_lib.object_post('custom_compliance_controls', json.dumps(compliance_control_data), esp_public, esp_secret)
    return compliance_control_new


def compliance_import(import_data, esp_public, esp_secret):
    for standard in import_data:
        organization_id = import_data[standard]['organization_id']
        name = standard
        description = import_data[standard]['compliance_standard_description']
        standard_created = compliance_standard_create(organization_id, name, description, esp_public, esp_secret)
        standard_created_id = int(standard_created['id'])
        for domain in import_data[standard]['domains']:
            custom_compliance_standard_id = standard_created_id
            name = domain
            identifier = import_data[standard]['domains'][domain]['compliance_domain_identifier']
            domain_created = compliance_domain_create(custom_compliance_standard_id, name, identifier, esp_public, esp_secret)
            domain_created_id = int(domain_created['id'])
            for control in import_data[standard]['domains'][domain]['controls']:
                custom_compliance_domain_id = domain_created_id
                name = control
                identifier = import_data[standard]['domains'][domain]['controls'][control]['compliance_control_identifier']
                description = import_data[standard]['domains'][domain]['controls'][control]['compliance_control_description']
                signature_ids = import_data[standard]['domains'][domain]['controls'][control]['signature_ids']
                custom_signature_ids = import_data[standard]['domains'][domain]['controls'][control]['custom_signature_ids']
                control_created = compliance_control_create(custom_compliance_domain_id, name, identifier, description, signature_ids, custom_signature_ids, esp_public, esp_secret)
    return 0


def signatures_combined_get(esp_public, esp_secret):
    # Get both built in and custom signatures
    signatures_built_in_list = esp_api_lib.object_list_get('signatures', esp_public, esp_secret)
    signatures_custom_list = esp_api_lib.object_list_get('custom_signatures', esp_public, esp_secret)

    # Check the signatures list from the server for duplicate ID's
    signatures_combined_dict = {}

    # Check and add for built-in sigs
    for signature in signatures_built_in_list:
        signature_identifier = signature['attributes']['identifier'].encode('utf-8')
        signature_id = int(signature['id'])
        signature_custom = False
        if signature_identifier not in signatures_combined_dict:
            signatures_combined_dict[signature_identifier] = {}
            signatures_combined_dict[signature_identifier]['signature_id'] = signature_id
            signatures_combined_dict[signature_identifier]['signature_custom'] = signature_custom
        else:
            esp_api_lib.exit_error('500', "Duplicate Signature Identifier found in the built-in signature list: " + json.dumps(signature))

    # Check and add for custom sigs
    for signature in signatures_custom_list:
        signature_identifier = signature['attributes']['identifier'].encode('utf-8')
        signature_id = int(signature['id'])
        signature_custom = True
        if signature_identifier not in signatures_combined_dict:
            signatures_combined_dict[signature_identifier] = {}
            signatures_combined_dict[signature_identifier]['signature_id'] = signature_id
            signatures_combined_dict[signature_identifier]['signature_custom'] = signature_custom
        else:
            esp_api_lib.exit_error('500', "Duplicate Signature Identifier found in the custom signature list: " + json.dumps(signature))
    return signatures_combined_dict


def signatures_id_from_identifier(import_dict, signatures_combined_dict):
    # Get a working copy
    import_dict_temp = import_dict.copy()

    # Look up the sigs and add to the main dict
    for standard in import_dict_temp:
        for domain in import_dict_temp[standard]['domains']:
            for control in import_dict_temp[standard]['domains'][domain]['controls']:
                for signature_identifier in import_dict_temp[standard]['domains'][domain]['controls'][control]['signature_identifier_list']:
                    if signatures_combined_dict[signature_identifier]['signature_custom'] == True:
                        import_dict[standard]['domains'][domain]['controls'][control]['custom_signature_ids'].append(signatures_combined_dict[signature_identifier]['signature_id'])
                    else:
                        import_dict[standard]['domains'][domain]['controls'][control]['signature_ids'].append(signatures_combined_dict[signature_identifier]['signature_id'])
    return import_dict_temp


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
        'importfile',
        type=str,
        help='File to Import from.')

    args = parser.parse_args()
    # --End parse command line arguments-- #

    # Sort out ESP API Key
    esp_public, esp_secret = esp_api_lib.settings_get(args.public, args.secret)

    # --Main-- #
    # Load the JSON file into Dict
    print()
    print('Loading the CSV data from the file...')
    compliance_from_csv = esp_api_lib.file_load_csv(args.importfile)

    # Get the Sig data
    print('API - Loading the signature data from ESP...')
    signatures_list_combined = signatures_combined_get(esp_public, esp_secret)

    # Parse, convert, and nest the CSV data
    print('Converting the CSV data into nested format for import...')
    compliance_structure = compliance_get(compliance_from_csv, esp_public, esp_secret)

    # Convert signatures from identifiers to ID's
    print('Converting signature identifiers to ID for import...')
    compliance_structure = signatures_id_from_identifier(compliance_structure, signatures_list_combined)

    # Import compliance
    print('API - Starting import into ESP...')
    import_result = compliance_import(compliance_structure, esp_public, esp_secret)
    print()
    print('Import Complete!')

