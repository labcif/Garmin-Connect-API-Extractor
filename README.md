# Garmin-Connect-API-Extractor (GCA-Extractor)

This is a script to extract data from Garmin Connect API related to a user.

## Requirements
 - ADB (Android Debug Bridge)
 - Python 3
 - Python modules: requests, json, argparse, datetime, time, os, sys, subprocess, http.client
 - Rooted Android device
 - Garmin Connect app installed on the device
 - Garmin Connect app logged in

## How it works

The script uses ADB to extract the Bearer token saved by Garmin Connect in its network log file (app.log).
Using that token it can access the Garmin Connect API and extract the data.

<img src="https://i.ibb.co/RSqhJGt/Diagrama-em-branco-P-gina-1-1.png" alt="Diagram" border="0">

## Parameters
    - a, --api: API to extract data from (currently activities, activity_details, sleep, stress, steps and heart_rate)
    - s, --start_date: Start date to extract data from (YYYY-MM-DD)
    - e, --end_date: End date to extract data from (YYYY-MM-DD)
    - i, --id: Activities IDs to extract data from (list of IDs can be obtained using the activities API)

## Usage

```bash
python3 gcaExtractor.py -a <API> -s <START_DATE> -e <END_DATE>
python3 gcaExtractor.py -a activity_details -i <ACTIVITY_ID>
```

## Example

```bash
    python3 gcaExtractor.py -a activities -s 2022-11-13 -e 2022-11-19
    python3 gcaExtractor.py -a activity_details -i 123456789, 987654321
```

## Output

The script will create a token.txt file with the Bearer token and a file or multiple files with the extracted data.

## Warning

This method is not 100% reliable and may stop working at any time. Also it is not guaranteed that the token extracted is still valid.

Also make sure you are only accessing data that you have permission (e.g. your own account). This script connects to the Garmin Connect
Servers, by using this script you are accepting the responsibilities for you own actions such at it is with any open source tool.

## Authors

Script created by Fabian Nunes for my Master's thesis, under the supervision of Prof. Dr. Miguel Frade and Prof. Dr. Patrício Rodrigues in Polytechnic Institute of Leiria.

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details