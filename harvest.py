
import requests
import os
from datetime import datetime, timedelta

worker = os.environ.get("WORKER")
if not worker:
    raise ValueError("Environment variable 'WORKER' is not set.")
token = os.environ.get("TOKEN")
if not token:
    raise ValueError("Environment variable 'TOKEN' is not set.")
barn = os.environ.get("BARN")
if not barn:
    raise ValueError("Environment variable 'BARN' is not set.")
pumpkin_field = os.environ.get("PUMPKIN_FIELD")
if not pumpkin_field:
    raise ValueError("Environment variable 'PUMPKIN_FIELD' is not set.")
harvest_spot = os.environ.get("HARVEST_SPOT")
if not harvest_spot:
    raise ValueError("Environment variable 'HARVEST_SPOT' is not set.")
harvest_action = os.environ.get("HARVEST_ACTION")
if not harvest_action:
    raise ValueError("Environment variable 'HARVEST_ACTION' is not set.")
pumpkin_query = os.environ.get("PUMPKIN_QUERY")
if not pumpkin_query:
    raise ValueError("Environment variable 'PUMPKIN_QUERY' is not set.")
pumpkin = os.environ.get("PUMPKIN")
if not pumpkin:
    raise ValueError("Environment variable 'PUMPKIN' is not set.")

def count_pumpkins_in_barn(token, barn, pumpkin_query, pumpkin):
    print(pumpkin)
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
    target_date = datetime.today()
    from_date = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0).isoformat() + 'Z'
    to_date = (target_date + timedelta(days=1)).isoformat() + 'Z'
    variables = {
        "username": worker,
        "from": from_date,
        "to": to_date
    }
    payload = {
        'query': pumpkin_query,
        'variables': variables
    }
    should_harvest = True
    response = requests.post(barn, headers=headers, json=payload)
    response.raise_for_status() # Raise an exception for bad status codes
    data = response.json()
    if 'errors' in data:
        print("GraphQL Errors:")
        for error in data['errors']:
            print(error)
    else:
        user_data = data.get('data', {}).get('user')
        nb_pumpkins = user_data.get(f"{pumpkin}sCollection").get(f"{pumpkin}Calendar").get(f"totalC{pumpkin[1:]}s")
        print(f" pumpkins: {nb_pumpkins}")
        if nb_pumpkins > 0:
            return False
        return True

def harvest_pumpkin(pumpkin_field, token):
    print("No harvests found today. Proceeding with the harvest.")
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
    harvestable_pumpkins_response = requests.get(pumpkin_field, headers=headers)
    if harvestable_pumpkins_response.status_code == 200:
        harvestable_pumpkins = harvestable_pumpkins_response.json()
        if harvestable_pumpkins:
            print(f"Found {len(harvestable_pumpkins)} ripe pumpkins to harvest.")
            for pumpkin in harvestable_pumpkins:
                pumpkin_id = pumpkin['number']
                pumpkin_name = pumpkin['title']
                print(f"Identifying Pumpkin #{pumpkin_id}")
            if len (harvestable_pumpkins) > 0:
                print(f"Pumpkin #{harvestable_pumpkins[-1]['number'] } is ripe.")
                harvest = f"{harvest_spot}{harvestable_pumpkins[-1]['number']}/{harvest_action}"
                print(harvest[1:])
                harvest_response = requests.put(harvest, headers=headers)
                if harvest_response.status_code == 200:
                    print(f"Successfully harvested Pumpkin #{harvestable_pumpkins[-1]['number']}.")
                else:
                    print(f"Failed to harvest Pumpkin #{harvestable_pumpkins[-1]['number']}. Status code: {harvest_response.status_code}")
        else:
            print("No pumpkin found.")
    else:
        print(f"Error fetching pumpkins. Status code: {harvestable_pumpkins_response.status_code}", "Response:", harvestable_pumpkins_response.text)

if count_pumpkins_in_barn(token, barn, pumpkin_query, pumpkin):
    harvest_pumpkin(pumpkin_field, token)
