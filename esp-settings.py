from __future__ import print_function
import esp_api_lib
import argparse


# --Execution Block-- #
if __name__ == '__main__':

    # --Parse command line arguments-- #
    parser = argparse.ArgumentParser(prog='esptoolbox')

    parser.add_argument(
        '-p',
        '--public',
        type=str,
        help='*Required* - ESP API Public Key that you want to set to access your ESP account.')

    parser.add_argument(
        '-s',
        '--secret',
        type=str,
        help='*Required* - ESP API Secret Key that you want to set to access your ESP account.')

    parser.add_argument(
        '-n',
        '--name',
        type=str,
        help='*Optional* - Name of the API key pair.')

    args = parser.parse_args()
    # --End parse command line arguments-- #

    # --Main-- #
    if args.public is not None and args.secret is not None:
        esp_api_lib.esp_settings_write(args.public, args.secret, args.name)
        print('Settings successfully saved to disk.')
    elif args.public is None and args.secret is None:
        esp_settings = esp_api_lib.esp_settings_read()
        if esp_settings['esp_name'] != '':
            print("Your currently configured ESP Public Key for " + esp_settings['esp_name'] + " is:")
            print(esp_settings['esp_public'])
        else:
            print("Your currently configured ESP Public Key is:")
            print(esp_settings['esp_public'])
    else:
        print(400)
        print("Please input both a public key (-p) as well as a secret key (-s) or leave both out to see currently set information.")
