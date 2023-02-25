# Garmin-Connect-API-Extractor

This is a script to extract data from Garmin Connect API related to an user.

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

<img src="https://i.ibb.co/Y8BfCTj/Diagrama-em-branco-2.png" alt="Diagrama-em-branco-2" border="0">

## Parameters
    - a, --api: API to extract data from (currently activities, activity_details, sleep, stress, steps and heart_rate)
    - s, --start_date: Start date to extract data from (YYYY-MM-DD)
    - e, --end_date: End date to extract data from (YYYY-MM-DD)
    - i, --id: Activities IDs to extract data from (list of IDs can be obtained using the activities API)

## Usage

```bash
python3 apiExtractor.py -a <API> -s <START_DATE> -e <END_DATE>
python3 apiExtractor.py -a activity_details -i <ACTIVITY_ID>
```

## Example

```bash
    python apiExtractor -a activities -s 2022-11-13 -e 2022-11-19
    python apiExtractor -a activity_details -i 123456789, 987654321
```

## Output

The script will create a token.txt file with the Bearer token and a file or multiple files with the extracted data.

## Warning

This method is not 100% reliable and may stop working at any time. Also it is not guaranteed that the token extracted is still valid.

## Authors

Script created by Fabian Nunes for my Master's thesis, under the supervision of Prof. Dr. Miguel Frade and Prof. Dr. Patrício Rodrigues in Polytechnic Institute of Leiria.

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details