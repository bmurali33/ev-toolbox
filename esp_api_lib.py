from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
from hashlib import sha1

import pycurl
import json
import hashlib
import base64
import cStringIO
import hmac
import time
import certifi
import sys
import urlparse
import csv
import os.path


# --Description-- #
# ESP API Helper library.  Used to contain the API calls.
# --End Description-- #


# --Configuration-- #
# Settings file name
DEFAULT_SETTINGS_FILE_NAME = "esp-settings.conf"
DEFAULT_SETTINGS_FILE_VERSION = 1
# --End Configuration-- #


# --Helper Methods-- #
# Exit handlers
def exit_error(error_code, error_message=None, system_message=None):
    print(error_code)
    if error_message is not None:
        print(error_message)
    if system_message is not None:
        print(system_message)
    sys.exit(1)


def exit_success():
    sys.exit(0)


# Update settings
def esp_settings_upgrade(old_settings):
    exit_error(500, "First version of the settings file - you should not have been able to get here.  Please recreate your settings file as something is wrong.")


# Read in settings
def esp_settings_read(settings_file_name=DEFAULT_SETTINGS_FILE_NAME, settings_file_version=DEFAULT_SETTINGS_FILE_VERSION):
    settings_file_name_and_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), settings_file_name)
    esp_settings = {}
    if os.path.isfile(settings_file_name_and_path):
        try:
            with open(settings_file_name_and_path, 'r') as f:
                esp_settings = json.load(f)
        except Exception as ex:
            exit_error(400, "Error in reading/parsing the esp-settings file.  Please reset the settings using the esp-settings.py utility.", ex)
        if esp_settings['esp_settings_version'] == settings_file_version:
            return esp_settings
        elif esp_settings['_esp_settings_version'] < settings_file_version:
            return esp_settings_upgrade(esp_settings)
        else:
            exit_error(500, "The settings file being used is newer than the utility understands.  "
                            "Please recreate the settings file using the esp-settings.py utility or "
                            "update the esp tools in use.")
    else:
        exit_error(400, "Cannot find the esp-settings file.  Please create one using the esp-settings.py utility.")


# Write settings to a file
def esp_settings_write(public, secret, name, settings_file_name=DEFAULT_SETTINGS_FILE_NAME, settings_file_version=DEFAULT_SETTINGS_FILE_VERSION):
    # Write settings file
    new_settings = {}
    new_settings['esp_settings_version'] = settings_file_version
    new_settings['esp_public'] = public
    new_settings['esp_secret'] = secret
    new_settings['esp_name'] = name
    settings_file_name_and_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), settings_file_name)
    try:
        with open(settings_file_name_and_path, 'w') as f:
            json.dump(new_settings, f)
    except Exception as ex:
        exit_error(500, "Failed to create settings file.", ex)


# Figure out the API Key settings
def settings_get(args_public, args_secret):
    esp_settings = {}
    if args_public is None or args_secret is None:
        esp_settings = esp_settings_read()
    if args_public is None:
        esp_public = esp_settings['esp_public']
    else:
        esp_public = args_public
    if args_secret is None:
        esp_secret = esp_settings['esp_secret']
    else:
        esp_secret = args_secret
    return esp_public, esp_secret


# Calculate time delta
def time_delta(time_start, time_end):
    return (time_end - time_start).total_seconds()


# Process API requests
def api_rate_wait(header_text):
    # Parse and store the header data
    headers = {}
    for line in header_text.splitlines():
        if ':' in line:
            name, value = line.split(':', 1)
            name = name.strip()
            value = value.strip()
            headers[name] = value

    # Calculate and sleep for the remaining retry window
    time_now = datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z')
    time_reset = datetime.strptime(headers['X-RateLimit-Reset'], '%Y-%m-%dT%H:%M:%SZ')
    time.sleep((time_reset - time_now).total_seconds())
    return None


def call_api(action, url, data, esp_public, esp_secret, count=0):
    # Construct ESP API URL
    ev_create_url = 'https://api.evident.io%s' % url

    # Create md5 hash of body
    m = hashlib.md5()
    m.update(data.encode('utf-8'))
    data_hash = base64.b64encode(m.digest())

    # Find Time
    now = datetime.now()
    stamp = mktime(now.timetuple())

    # Create Authorization Header
    canonical = '%s,application/vnd.api+json,%s,%s,%s' % (action, data_hash, url, format_date_time(stamp))

    hashed = hmac.new(esp_secret, canonical, sha1)
    auth = hashed.digest().encode("base64").rstrip('\n')

    # Create Curl request
    buf_body = cStringIO.StringIO()
    buf_header = cStringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.CAINFO, certifi.where())
    c.setopt(pycurl.URL, str(ev_create_url))
    c.setopt(pycurl.HTTPHEADER, [
        'Date: %s' % format_date_time(stamp),
        'Content-MD5: %s' % data_hash,
        'Content-Type: application/vnd.api+json',
        'Accept: application/vnd.api+json',
        'Authorization: APIAuth %s:%s' % (esp_public, auth)])
    c.setopt(c.WRITEFUNCTION, buf_body.write)
    c.setopt(c.HEADERFUNCTION, buf_header.write)

    if action == 'POST':
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
    elif action == 'PATCH':
        c.setopt(c.CUSTOMREQUEST, 'PATCH')
        c.setopt(pycurl.POSTFIELDS, data)
    c.perform()
    ev_response_header_text = buf_header.getvalue()
    ev_response_body_json = buf_body.getvalue()
    buf_header.close()
    buf_body.close()
    c.close()
    ev_response_body = json.loads(ev_response_body_json)

    # Handle rate-limit exceptions
    if 'errors' in ev_response_body:
        for error in ev_response_body['errors']:
            if int(error['status']) == 429:
                # Check the number of times this has been attempted
                if count < 5:
                    # Enter into the wait state requested by the server
                    api_rate_wait(ev_response_header_text)
                    count += 1
                    # print("retry - %s" % count)
                    return call_api(action, url, data, esp_public, esp_secret, count)
                else:
                    # Give-up after retrying too many times
                    exit_error(429, 'Stuck in a rate limit lock - exiting!')
            else:
                # Throw Exception and end script if any other error occurs
                print('Error occurred on data package:')
                print(data)
                print()
                raise Exception('%d - %s' % (int(error['status']), error['title']))
    return ev_response_body


def url_parse(url):
    return urlparse.parse_qs(urlparse.urlparse(url).query)


def page_parse(url):
    url_dict = url_parse(url)
    return int(url_dict['page[number]'][0])


def url_create(api_url, page_size=100, page_number=1):
    return api_url + '?page[size]=%s&page[number]=%d' % (page_size, page_number)


# Get id from relationship link
# Example: http://test.host/api/v2/signatures/1003.json
# Should return 1003
def get_id_from_link(link):
    a = link.split("/")
    b = a[len(a) - 1].split(".")
    return int(b[0])


# Get Object Lists (Complete)
def object_list_get(api_object_name, public, secret, data='', page_size=100):
    api_url = '/api/v2/' + api_object_name
    page_number = 1
    objects_list = []

    while True:
        url = url_create(api_url, page_size, page_number)
        api_response = call_api('GET', url, data, public, secret)
        objects_list.extend(api_response['data'])
        if 'next' in api_response['links']:
            page_number = page_parse(api_response['links']['next'])
        else:
            break
    return objects_list


# Get Single Object
def object_get(api_object_name, public, secret, data=''):
    api_url = '/api/v2/' + api_object_name
    url = url_create(api_url)
    api_response = call_api('GET', url, data, public, secret)
    return api_response['data']


# Create Object
def object_post(api_object_name, data, public, secret):
    api_url = '/api/v2/' + api_object_name
    url = url_create(api_url)
    api_response = call_api('POST', url, data, public, secret)
    return api_response['data']


# Update Object
def object_patch(api_object_name, data, public, secret):
    api_url = '/api/v2/' + api_object_name
    url = url_create(api_url)
    api_response = call_api('PATCH', url, data, public, secret)
    return api_response['data']


# Load the JSON file into Dict
def file_load_csv(file_name):
    csv_list = []
    with open(file_name, 'rb') as csv_file:
        file_reader = csv.DictReader(csv_file)
        for row in file_reader:
            csv_list.append(row)
    return csv_list


# Print to CSV
def print_to_csv(object_list):
    keys = object_list[0].keys()
    dict_writer = csv.DictWriter(sys.stdout, keys, lineterminator='\n')
    dict_writer.writeheader()
    dict_writer.writerows(object_list)


# Print to JSON
def print_to_json(object_list):
    print(json.dumps(object_list))


# Write CSV to file
def write_to_csv(object_list, file_name, field_names=None):
    if field_names is None:
        field_names = object_list[0].keys()
    file_name_and_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
    try:
        with open(file_name_and_path, 'w') as f:
            dict_writer = csv.DictWriter(f, field_names, lineterminator='\n', extrasaction='ignore')
            dict_writer.writeheader()
            dict_writer.writerows(object_list)
    except Exception as ex:
        exit_error(500, "Failed to create export file.", ex)


# Write JSON to file
def write_to_json(object_list, file_name):
    file_name_and_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
    try:
        with open(file_name_and_path, 'w') as f:
            json.dump(object_list, f)
    except Exception as ex:
        exit_error(500, "Failed to create export file.", ex)

# --End Helper Methods-- #
