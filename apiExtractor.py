#!/usr/bin/python

# Author: Fabian Nunes
# Date: 2023-02-24
# Version: 1.1
# Script to get data from the API Garmin Connect Android App for a specific user and date range
# The script uses the ADB tool to get the token from the device and then uses the token to get the data from the API
# In case of extracting the activity details, the script will accept a list of IDs
# Example: python apiExtractor.py -a activities -s 2022-11-13 -e 2022-11-19
# Example: apiExtractor.py -a activity_details -i 9981299874, 9981299875
# Works on Windows and Unix

import http.client
import os
import subprocess
import sys
import time
from datetime import date, timedelta
import argparse


class Bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'


def date_range(start_date, end_date):
    delta = timedelta(days=1)
    while start_date <= end_date:
        yield start_date
        start_date += delta


def start_warning():
    print(Bcolors.WARNING + "[WARNING] This script connects to the Garmin Connect Servers to extract data! \n"
                            "Before continuing make sure you are only accessing data you have permission to.\n"
                            "By using this script you are accepting that you are responsible for your own action!")
    choice = input("Do you wish to continue (Y/N): ")
    if choice.lower() == "y":
        print(Bcolors.OKGREEN + "[START] Starting Script")
    else:
        print(Bcolors.FAIL + "[END] Closing Script")
        print(Bcolors.ENDC)
        sys.exit()


endpoints = {
    "sleep": "/wellness-service/wellness/dailySleepDataCharts",
    "heart_rate": "/mobile-gateway/snapshot/timeline/v2/forDate/",
    "activities": "/activitylist-service/activities/search/activities",
    "activity_details": "/activity-service/activity/",
    "stress": "/usersummary-service/stats/stress/daily/",
    "steps": "/mobile-gateway/snapshot/timeline/v2/forDate/",
    "daily": "/mobile-gateway/snapshot/timeline/v2/forDate/",
}

parser = argparse.ArgumentParser(description='Extract data from the Garmin Connect API')
parser.add_argument('-a', '--api', help='API to extract', required=True, choices=endpoints.keys())
parser.add_argument('-s', '--start_date', help='Start date', required=False)
parser.add_argument('-e', '--end_date', help='End date', required=False)
# array of ids
parser.add_argument('-i', '--id', help='Activity ids', required=False, nargs='+')
args = parser.parse_args()

# get api
api = args.api
start_warning()
if api == "activity_details":
    # check if argument is passed
    if args.id is None:
        print("Please specify the activity id")
        sys.exit()
    id_act = args.id
    # split by ,
    id_act = id_act[0].split(",")
    # check if there is only one id
    if len(id_act) == 1:
        # check if there is a comma at the end
        if id_act[0][-1] == ",":
            id_act[0] = id_act[0][:-1]
        # check if there is a comma at the beginning
        if id_act[0][0] == ",":
            id_act[0] = id_act[0][1:]
        # check if there is a comma at the beginning and at the end
        if id_act[0][0] == "," and id_act[0][-1] == ",":
            id_act[0] = id_act[0][1:-1]
    # check if there are more than one id
    if len(id_act) > 1:
        # check if there is a comma at the end
        if id_act[-1][-1] == ",":
            id_act[-1] = id_act[-1][:-1]
        # check if there is a comma at the beginning
        if id_act[0][0] == ",":
            id_act[0] = id_act[0][1:]
        # check if there is a comma at the beginning and at the end
        if id_act[0][0] == "," and id_act[0][-1] == ",":
            id_act[0] = id_act[0][1:-1]
        # check if there is a comma at the end

else:
    if args.start_date is None or args.end_date is None:
        print("Please specify the start and end dates")
        sys.exit()
    start_date = args.start_date
    end_date = args.end_date
    # Check if the dates are valid and the start date is before the end date
    try:
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)
        if start_date > end_date:
            print("The start date should be before the end date")
            sys.exit()
    except ValueError:
        print("The date is not valid. Please use the format YYYY-MM-DD")
        sys.exit()
    dates = [d.strftime("%Y-%m-%d") for d in
             date_range(date.fromisoformat(str(start_date)), date.fromisoformat(str(end_date)))]

conn = http.client.HTTPSConnection("connectapi.garmin.com")

# Check if the device is connected
adb_cmd = "adb devices"
output = subprocess.run(adb_cmd, stdout=subprocess.PIPE, shell=True)
output = output.stdout.decode("utf-8").strip()
if "List of devices attached" in output and "device" not in output:
    print(Bcolors.FAIL + "[ERROR] No device connected")
    print(Bcolors.ENDC)
    sys.exit()

# Check if the device is rooted
adb_cmd = "adb shell su -c id"
output = subprocess.run(adb_cmd, stdout=subprocess.PIPE, shell=True)
output = output.stdout.decode("utf-8").strip()
if "uid=0(root)" not in output:
    print(Bcolors.FAIL + "[ERROR] Device is not rooted")
    print(Bcolors.ENDC)
    sys.exit()

# Check if the device has the Garmin Connect Mobile app installed
if os.name == 'nt':
    adb_cmd = "adb shell su -c pm list packages | findstr com.garmin.android.apps.connectmobile"
else:
    adb_cmd = "adb shell su -c pm list packages | grep com.garmin.android.apps.connectmobile"
output = subprocess.run(adb_cmd, stdout=subprocess.PIPE, shell=True)
output = output.stdout.decode("utf-8").strip()
if "com.garmin.android.apps.connectmobile" not in output:
    print(Bcolors.FAIL + "[ERROR] Garmin Connect Mobile app is not installed")
    print(Bcolors.ENDC)
    sys.exit()

print(Bcolors.OKBLUE + "[INFO] Device is connected and rooted")
print(Bcolors.OKBLUE + "[INFO] Extracting the current bearer token")
adb_cmd = "adb -d shell su -c cat /data/data/com.garmin.android.apps.connectmobile/files/logs/app.log"

# Check if there already is a token file
if os.path.exists("token.txt"):
    # Ask the user if they want to use the existing token
    print(Bcolors.OKBLUE + "[INFO] A token file already exists")
    use_existing_token = input("Do you want to use the existing token? (y/n): ")
    if use_existing_token.lower() == "y":
        bearer_token = open("token.txt", "r").read()
        print(Bcolors.OKBLUE + "[INFO] Using the existing token")
    else:
        # Run the ADB command and store the output
        output = subprocess.run(adb_cmd, stdout=subprocess.PIPE, shell=True)
        output = output.stdout.decode("utf-8").strip()
        # Get Extract strings that begin with "Authorization: Bearer"
        for line in output.splitlines():
            if line.startswith('Authorization: Bearer'):
                # Split the line to get the bearer token
                bearer_token = line.split(" ")[-1]
        print(Bcolors.OKBLUE + "[INFO] The bearer token was extracted. Saving the bearer token to a file")
# Print the bearer token
# print("Bearer token:", bearer_token)
# save the bearer token to a file
with open('token.txt', 'w') as f:
    f.write(bearer_token)
    f.close()

print(Bcolors.OKGREEN + "[SUCCESS] The bearer token was saved to the file token.txt")

# create garmin.api folder if it doesn't exist
if not os.path.exists("garmin.api"):
    os.makedirs("garmin.api")

print(Bcolors.OKBLUE + "[INFO] Getting the data from the Garmin Connect API")

payload = ''
headers = {
    'Authorization': 'Bearer ' + bearer_token,
}

if api == "heart_rate" or api == "steps" or api == "daily":
    # Loop through the dates and get the data for each date
    for date in dates:
        print(Bcolors.OKBLUE + "[INFO] Getting the " + api + " data for the date " + date)
        conn.request("GET", endpoints[api] + date, payload, headers)
        res = conn.getresponse()
        if res.status != 200:
            print(Bcolors.FAIL + "[ERROR] Error getting the data from the Garmin Connect API")
            print(Bcolors.ENDC)
        else:
            print(Bcolors.OKBLUE + "[INFO] Request to the Garmin Connect API was successful. Saving the data to a file")
            data = res.read()
            # Save the data to a file
            filename = "./garmin.api/" + api + "_" + date + ".json"
            with open(filename, 'w') as f:
                f.write(data.decode("utf-8"))
                f.close()
        # Sleep for 1 second to avoid getting blocked by Garmin
        print(Bcolors.OKBLUE + "[INFO] Sleeping for 1 second to avoid getting blocked by Garmin")
        time.sleep(1)
    print(Bcolors.OKGREEN + "[SUCCESS] The data was saved to the files " + api + ".json. Script finished")
    print(Bcolors.ENDC)
elif api == "activity_details":
    # Loop through the ids and get the data for each id
    for id in id_act:
        print(Bcolors.OKBLUE + "[INFO] Getting the " + api + " data for the id " + id)
        url = endpoints[api] + id + "/details"
        conn.request("GET", url, payload, headers)
        res = conn.getresponse()
        if res.status != 200:
            print(Bcolors.FAIL + "[ERROR] Error getting the data from the Garmin Connect API")
            print(Bcolors.ENDC)
        else:
            print(Bcolors.OKBLUE + "[INFO] Request to the Garmin Connect API was successful. Saving the data to a file")
            data = res.read()
            # Save the data to a file
            filename = "./garmin.api/" + api + '_' + id + '.json'
            with open(filename, 'w') as f:
                f.write(data.decode("utf-8"))
                f.close()
        # Sleep for 1 second to avoid getting blocked by Garmin
        print(Bcolors.OKBLUE + "[INFO] Sleeping for 1 second to avoid getting blocked by Garmin")
        time.sleep(1)
    print(Bcolors.OKGREEN + "[SUCCESS] The data was saved to the files " + api + ".json. Script finished")
    print(Bcolors.ENDC)
else:
    if api == "stress":
        conn.request("GET", endpoints[api] + str(start_date) + "/" + str(end_date),
                     payload, headers)
    else:
        conn.request("GET", endpoints[api] + "?startDate=" + str(start_date) + "&endDate=" + str(end_date),
                     payload, headers)
    res = conn.getresponse()
    if res.status != 200:
        print(Bcolors.FAIL + "[ERROR] Error getting the data from the Garmin Connect API")
        print(Bcolors.ENDC)
        sys.exit()

    print(Bcolors.OKBLUE + "[INFO] Request to the Garmin Connect API was successful. Saving the data to a file")
    data = res.read()
    # Save the data to a file
    file_name = "./garmin.api/" + api + "_" + str(start_date) + "-" + str(end_date) + ".json"
    with open(file_name, 'w') as f:
        f.write(data.decode("utf-8"))
        f.close()

    print(Bcolors.OKGREEN + "[SUCCESS] The data was saved to the file " + file_name + ". Script finished")
    print(Bcolors.ENDC)
