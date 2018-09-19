# ev-toolbox

There are multiple tools that can be used (listed below).  Everything here is written in Python (2.7, specifically - and required at this time).

If you need to install python, you can get more information at [Python's Page](https://www.python.org/).  I also highly recommend you install the [PIP package manager for Python](https://pypi.python.org/pypi/pip) if you do not already have it installed.

Please note: This works in Python 2.7.x.  This does NOT currently work in Python 3.  There are a couple of libraries in use which do not exist in 3.  No specific reason here (if you need a Python 3 version, let me know and I can look into replacing some of the libs - there will be some time involved to make this all work though).

To check your Python version:
```
python --version
```
It should say Python 2.7.x.  If it says 3.anything then you need to load 2.7 (as well or in its place, etc.).

To set up your python environment, you will need the following packages:
- pycurl
- certifi

To install/check for these:
```
pip install pycurl
pip install certifi
```

Everything below should work (unless specifically called out) with a standard "Manager" level user in ESP.

------------------------------------------------------------------

On to the tools themselves (Everything requires the esp_api_lib.py library file - keep it in the same directory as the other tools):

**esp-settings.py**
- Use this to set up your ESP API key for use in the remaining tools.  You add the -p and -s switch with your API keys generated from the ESP Web UI.  Please do not add any ' or " to the keys as it will store the exact thing you type/paste in.  -n can be used to name the key to help you remember which one you are using, but it is optional (and you can use ticks or quotes for this one - it is not actually used for anything, just to remind you what key is in use).
- Also you can run this without any args to see what key is being used.

NOTE: This is stored in clear JSON text in the same folder as the tools.  Keep the resulting conf file protected and do not give it out to anyone.

Example:
```
python esp-settings.py -p 7/djkfskjdfhsksjdhfskjdhfskjdhfksjdhfksjdhfkjshdfkjshdfkjhsdkjfhsdkjfhskjdhfskdjhfSk+g== -s 4Hsjdksd8923hri4bfsdvs98ery4phterhgpsdf8vy7e4htpw4tp9gher07ghpe4hgoei4jgp98erg0s4uhtdg== -n esp-toolbox-api-key
```

**esp-compliance-export.py**
- Use this to export the compliance (templates) from your ESP environment.  This can export both built-in compliance frameworks as well as custom compliance frameworks (it is all filtered by name).  The required arguments are the export file name (and path, if needed) and the compliance standard name search string.
- Compliance standard name search string: This will be the name of the standard you want to export.  Because I can never remember the exact names, I added the ability to use wildcards (* for multiple characters and ? for single).  Basically this lets you do stuff like nist* or *800-171*, etc. and it will sort it out for you.
- Add the -blank switch if you just want an empty template for entering everything new.
- Add the -complete switch if you just want to export all of the fields.  Technically this can be used for import as well, but it is painful to work with.
- Add the -json switch to export into JSON (Complete) instead of CSV (not used for import - there in case you need to export the data and use it programmatically).

NOTE: The templates will contain a "signature_name" field at the end.  This is NOT required for import, it is simply there to make things more human readable.  EVERYTHING else is required for every line.

Example to export the NIST 800-53 report into a file called nist-800-53-export.csv:
```
python esp-compliance-export.py nist-800-53-export.csv "nist 800-53*"
```

Example to export the Soc2 report into a file called soc2-export.csv:
```
python esp-compliance-export.py soc2-export.csv *soc2*
```

Example to export a blank template into a file called esp-compliance-template.csv:
```
python esp-compliance-export.py esp-compliance-template.csv anything -blank
```

**esp-compliance-import.py**
- Use this to import from the compliance CSV template you have filled out (or modified).  This will read the CSV and try to format and import it into ESP as a NEW compliance standard (and domains and controls).  This tool cannot be used to update an existing compliance report.
- Required: import file name (and path, if needed)

NOTE: The CSV for import must be fully filled out (except for signature name).  If anything is missing or inconsistent, then it is a dice roll as to what gets imported (this does some basic validation, but bad data in will give you bad data out).  It tries to catch the worst offenders, but it is not perfect.

NOTE: The import will create multiple standards off of a single sheet, if that is what you have provided, so try to avoid typos...

A quick note about signature identifiers - this tools expects you to NOT have any duplicate signature identifiers in your lists of signatures (both built-in and custom).  If you did create a signature with the same identifier, this will detect that and error out before importing.  Please let me know if this is an issue for you, but be warned, there is no simple solution to this (the only unique ID for a signature is the DB ID number which is not in the web UI and is a real pain to track).

Example to import my nist-800-53-export.csv template:
```
python esp-compliance-import.py nist-800-53-export.csv
```

**esp-signatures-export.py**
- Use this to export the signatures list from ESP into CSV/JSON format.
- Options are -custom for only custom signatures and -builtin for only the built-in signatures.  For JSON format, use the -json switch.

Example to export all signatures into CSV file called esp-signatures.csv:
```
python esp-signatures-export.py esp-signatures.csv
```

Let me know if you have any questions, feedback, bugs, etc.
