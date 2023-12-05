import json

from src import driver

with open('/Users/zachbrown/Desktop/Work/Desi/Tech/Code/firebase_backups/backup_10_30_23.json') as fh:
    data = json.load(fh)

collections = data['__collections__']

del collections['AuthorizedEmails']
del collections['Globals']
del collections['Communities']


for driver_id in collections['Drivers'].keys():
    for key in ['first_name', 'last_name', 'full_name', 'display_name', 'phone_number', 'email', 'username', 'venmo_username', "profile_pic"]:
        if key in collections['Drivers'][driver_id]:
            del collections['Drivers'][driver_id][key]

for ride_id in collections['Rides'].keys():
    for key in ['first_name', 'last_name', 'full_name', 'display_name', 'phone_number', 'email', 'username', 'venmo_username', "profile_pic"]:
        if key in collections['Rides'][ride_id].get('driver',{}):
            del collections['Rides'][ride_id]['driver'][key]



with open('./data/backup.json', 'w') as fh:
    json.dump(data, fh)