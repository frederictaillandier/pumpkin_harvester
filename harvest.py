# Small halloween project to harvest pumpkins
# This script is designed to check if a worker has already harvested pumpkins today and, if not, proceed to harvest ripe pumpkins.

import requests
from datetime import date
import os

worker = os.environ.get("WORKER")
if not worker:
    raise ValueError("Environment variable 'WORKER' is not set.")
token = os.environ.get("TOKEN")
if not token:
    raise ValueError("Environment variable 'TOKEN' is not set.")
api_url = os.environ.get("BARN")
if not api_url:
    raise ValueError("Environment variable 'BARN' is not set.")
pumpkin_field = os.environ.get("PUMPKIN_FIELD")
if not pumpkin_field:
    raise ValueError("Environment variable 'PUMPKIN_FIELD' is not set.")
tractor = os.environ.get("TRACTOR")
if not tractor:
    raise ValueError("Environment variable 'TRACTOR' is not set.")
trailer = os.environ.get("TRAILER")
if not trailer:
    raise ValueError("Environment variable 'TRAILER' is not set.")
pitchfork = os.environ.get("PITCHFORK")
if not pitchfork:
    raise ValueError("Environment variable 'PITCHFORK' is not set.")
harvest_spot = os.environ.get("HARVEST_SPOT")
if not harvest_spot:
    raise ValueError("Environment variable 'HARVEST_SPOT' is not set.")
harvest_action = os.environ.get("HARVEST_ACTION")
if not harvest_action:
    raise ValueError("Environment variable 'HARVEST_ACTION' is not set.")

headers = {
    "Accept": pitchfork,
    "Authorization": f"Bearer {token}",
    tractor: trailer
}

try:
    response = requests.get(api_url, headers=headers, params={'state': 'all', 'page': 1, 'per_page': 100})
    should_harvest = True

    if response.status_code == 200:
        events = response.json()
        if events:
            today = date.today()
            todays_harvest = [event for event in events if 'created_at' in event and event['created_at'].startswith(str(today))]
            if todays_harvest:
                print(f"Today ({today}): {len(todays_harvest)} harvest(s) done.")
                should_harvest = False
            else:
                print(f"Today ({today}): No harvest done.")
        else:
            print("No harvests done for this worker.")

    elif response.status_code == 404:
        print(f"Error: Worker '{worker}' not found or no harvests done.")
    elif response.status_code == 401:
         print("Error: Unauthorized. Check your token permissions.")
    else:
        print(f"Error: Failed to fetch harvests. Status code: {response.status_code}")
        print(f"Response body: {response.text}")

    if should_harvest:
        print("No harvests found today. Proceeding with the harvest.")
        harvestable_pumpkin_url = pumpkin_field
        harvestable_pumpkins_response = requests.get(harvestable_pumpkin_url, headers=headers)
        if harvestable_pumpkins_response.status_code == 200:
            harvestable_pumpkins = harvestable_pumpkins_response.json()
            if harvestable_pumpkins:
                print(f"Found {len(harvestable_pumpkins)} ripe pumpkins to harvest.")
                for pumpkin in harvestable_pumpkins:
                    pumpkin_id = pumpkin['number']
                    pumpkin_name = pumpkin['title']
                    print(f"Identifying Pumpkin #{pumpkin_id}: {pumpkin_name}")
                if len (harvestable_pumpkins) > 0:
                    print(f"Pumpkin #{harvestable_pumpkins[-1]['number'] } is ripe.")
                    harvest = f"{harvest_spot}{harvestable_pumpkins[-1]['number']}/{harvest_action}"
                    merge_response = requests.put(harvest, headers=headers)
                    if merge_response.status_code == 200:
                        print(f"Successfully harvested Pumpkin #{harvestable_pumpkins[-1]['number']}.")
                    else:
                        print(f"Failed to harvest Pumpkin #{harvestable_pumpkins[-1]['number']}. Status code: {merge_response.status_code}")
            else:
                print("No pumpkin found.")
        else:
            print(f"Error fetching pumpkins. Status code: {harvestable_pumpkins_response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred during the request: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
